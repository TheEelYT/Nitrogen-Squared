// SPDX-License-Identifier: GPL-3.0-or-later
// Original portable host. Frontend attribution: ../UPSTREAM.md.
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
use serde_json::{json, Value};
use std::{
    collections::HashMap,
    io::{BufRead, BufReader, Write},
    path::PathBuf,
    process::{Child, ChildStdin, Command, Stdio},
    sync::{
        atomic::{AtomicU64, Ordering},
        mpsc, Arc, Mutex,
    },
    time::Duration,
};
use tauri::{Emitter, Manager};
use tauri_plugin_dialog::DialogExt;

type Reply = mpsc::Sender<Result<Value, String>>;
struct Bridge {
    input: Mutex<ChildStdin>,
    child: Mutex<Child>,
    pending: Mutex<HashMap<u64, Reply>>,
    sequence: AtomicU64,
    testing: bool,
}
impl Bridge {
    fn request(&self, command: &str, args: Value) -> Result<Value, String> {
        let id = self.sequence.fetch_add(1, Ordering::Relaxed);
        let (tx, rx) = mpsc::channel();
        self.pending
            .lock()
            .map_err(|_| "Backend state unavailable")?
            .insert(id, tx);
        let written = self
            .input
            .lock()
            .map_err(|_| "Backend unavailable".to_string())
            .and_then(|mut input| {
                writeln!(input, "{}", json!({"id":id,"command":command,"args":args}))
                    .and_then(|_| input.flush())
                    .map_err(|e| e.to_string())
            });
        if let Err(error) = written {
            self.pending.lock().unwrap().remove(&id);
            return Err(error);
        }
        let result = rx.recv_timeout(Duration::from_secs(30)).map_err(|_| {
            "Launcher backend did not respond. See .local/launcher-error.log.".to_string()
        });
        self.pending.lock().unwrap().remove(&id);
        result?
    }
}
fn backend(app: &tauri::AppHandle) -> Result<Arc<Bridge>, Box<dyn std::error::Error>> {
    let args: Vec<String> = std::env::args().collect();
    let flag = |name: &str| args.windows(2).find(|a| a[0] == name).map(|a| a[1].clone());
    let root = flag("--root").map(PathBuf::from).unwrap_or(
        std::env::current_exe()?
            .parent()
            .ok_or("No launcher directory")?
            .to_path_buf(),
    );
    let testing = args.iter().any(|s| s == "--self-test");
    std::fs::create_dir_all(root.join(".local"))?;
    let log = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(root.join(".local/launcher-error.log"))?;
    let python = if cfg!(windows) {
        root.join("support/python/python.exe")
    } else {
        PathBuf::from("python3")
    };
    let mut command = Command::new(python);
    command
        .args(["-I", "-X", "utf8", "-B"])
        .arg(root.join("app/tools/launcher_service.py"))
        .arg("--root")
        .arg(&root)
        .arg("--launcher-pid")
        .arg(std::process::id().to_string())
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::from(log))
        .current_dir(&root);
    command.env_remove("PYTHONHOME").env_remove("PYTHONPATH");
    if testing {
        command.arg("--self-test");
        command
            .arg("--report")
            .arg(flag("--report").ok_or("Self-test needs --report")?);
    }
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        command.creation_flags(0x08000000); // CREATE_NO_WINDOW; stdout is the local protocol pipe.
    }
    let mut child = command.spawn()?;
    let stdout = child.stdout.take().ok_or("No backend output")?;
    let input = child.stdin.take().ok_or("No backend input")?;
    let bridge = Arc::new(Bridge {
        input: Mutex::new(input),
        child: Mutex::new(child),
        pending: Mutex::new(HashMap::new()),
        sequence: AtomicU64::new(1),
        testing,
    });
    let reader = bridge.clone();
    let app = app.clone();
    std::thread::spawn(move || {
        for line in BufReader::new(stdout).lines() {
            let Ok(line) = line else { break };
            let Ok(value) = serde_json::from_str::<Value>(&line) else {
                continue;
            };
            if let Some(id) = value["id"].as_u64() {
                if let Some(tx) = reader.pending.lock().unwrap().remove(&id) {
                    let result = if let Some(error) = value["error"].as_str() {
                        Err(error.to_owned())
                    } else {
                        Ok(value["result"].clone())
                    };
                    let _ = tx.send(result);
                }
            } else if let Some(event) = value["event"].as_str() {
                let _ = app.emit(event, value["payload"].clone());
            }
        }
        for (_, tx) in reader.pending.lock().unwrap().drain() {
            let _ = tx.send(Err(
                "Launcher backend stopped. See .local/launcher-error.log.".into(),
            ));
        }
        let _ = app.emit("backend-exit", ());
    });
    Ok(bridge)
}
#[tauri::command]
async fn request(
    command: String,
    args: Option<Value>,
    bridge: tauri::State<'_, Arc<Bridge>>,
) -> Result<Value, String> {
    // Shutdown/update finalization and reports belong to the native host.
    if matches!(
        command.as_str(),
        "close" | "finalize_update" | "restore" | "self_test"
    ) {
        return Err("Use the native lifecycle action".into());
    }
    let bridge = bridge.inner().clone();
    tauri::async_runtime::spawn_blocking(move || {
        bridge.request(&command, args.unwrap_or(json!({})))
    })
    .await
    .map_err(|e| e.to_string())?
}
#[tauri::command]
async fn choose_disc(
    app: tauri::AppHandle,
    bridge: tauri::State<'_, Arc<Bridge>>,
) -> Result<Value, String> {
    let bridge = bridge.inner().clone();
    tauri::async_runtime::spawn_blocking(move || {
        let Some(path) = app
            .dialog()
            .file()
            .set_title("Select your N2O CUE sheet")
            .add_filter("CUE sheet (recommended)", &["cue"])
            .add_filter("BIN with matching CUE", &["bin"])
            .blocking_pick_file()
        else {
            return Ok(Value::Null);
        };
        let path = path.into_path().map_err(|_| "Select a local CUE file")?;
        bridge.request("choose", json!({"path":path}))
    })
    .await
    .map_err(|e| e.to_string())?
}
#[tauri::command]
fn host_info(bridge: tauri::State<'_, Arc<Bridge>>) -> Value {
    json!({"testing":bridge.testing,"channel":option_env!("N2_LAUNCHER_CHANNEL").unwrap_or("dev")})
}
#[tauri::command]
async fn lifecycle(
    action: String,
    ui: Option<Value>,
    app: tauri::AppHandle,
    bridge: tauri::State<'_, Arc<Bridge>>,
) -> Result<(), String> {
    if !matches!(action.as_str(), "restore" | "finalize_update" | "self_test") {
        return Err("Unsupported lifecycle action".into());
    }
    if action == "self_test" && !bridge.testing {
        return Err("Self-test mode required".into());
    }
    let bridge = bridge.inner().clone();
    tauri::async_runtime::spawn_blocking(move || bridge.request(&action, json!({"ui":ui})))
        .await
        .map_err(|e| e.to_string())??;
    app.exit(0);
    Ok(())
}
fn fatal(message: &str) -> ! {
    #[cfg(windows)]
    {
        #[link(name = "user32")]
        extern "system" {
            fn MessageBoxW(
                window: *mut std::ffi::c_void,
                text: *const u16,
                caption: *const u16,
                kind: u32,
            ) -> i32;
        }
        let text: Vec<u16> = message.encode_utf16().chain(Some(0)).collect();
        let caption: Vec<u16> = "Nitrogen Squared".encode_utf16().chain(Some(0)).collect();
        unsafe {
            MessageBoxW(std::ptr::null_mut(), text.as_ptr(), caption.as_ptr(), 0x10);
        }
    }
    eprintln!("{message}");
    std::process::exit(1)
}
fn main() {
    let args: Vec<String> = std::env::args().collect();
    // Preserve the command-line fixture used by portable CI without opening a webview.
    if args
        .iter()
        .any(|a| a == "--runtime-fixture" || a == "--bootstrap-tools")
    {
        let root = std::env::current_exe()
            .unwrap()
            .parent()
            .unwrap()
            .to_path_buf();
        let python = if cfg!(windows) {
            root.join("support/python/python.exe")
        } else {
            PathBuf::from("python3")
        };
        let status = Command::new(python)
            .args(["-I", "-X", "utf8", "-B"])
            .arg(root.join("app/tools/portable_launcher.py"))
            .arg("--root")
            .arg(root)
            .args(&args[1..])
            .status();
        std::process::exit(status.ok().and_then(|s| s.code()).unwrap_or(1));
    }
    let app=tauri::Builder::default().plugin(tauri_plugin_dialog::init())
        .setup(|app|{let bridge=backend(app.handle())?;app.manage(bridge);Ok(())})
        .invoke_handler(tauri::generate_handler![request,choose_disc,host_info,lifecycle])
        .on_window_event(|window,event|if let tauri::WindowEvent::CloseRequested{api,..}=event {
            api.prevent_close();let app=window.app_handle().clone();let bridge=app.state::<Arc<Bridge>>().inner().clone();
            std::thread::spawn(move||match bridge.request("close",json!({})) {
                Ok(_)=>app.exit(0),Err(error)=>{let _=app.emit("close-blocked",error);}
            });
        }).build(tauri::generate_context!()).unwrap_or_else(|error|fatal(&format!("Could not start Nitrogen Squared: {error}\n\nExtract the complete package. Windows requires Microsoft Edge WebView2. Details: .local/launcher-error.log.")));
    app.run(|app, event| {
        if let tauri::RunEvent::Exit = event {
            if let Some(bridge) = app.try_state::<Arc<Bridge>>() {
                let _ = bridge.child.lock().unwrap().kill();
            }
        }
    });
}
