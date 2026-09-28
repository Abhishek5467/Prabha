#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
use serde_json::Value;
use tauri_plugin_shell::ShellExt;

#[tauri::command]
async fn simulate(app: tauri::AppHandle, payload: Value) -> Result<Value, String> {
    let request = serde_json::to_string(&payload).map_err(|e| e.to_string())?;
    // Keep below Windows command-line limits. The executable is fixed, never user-selected.
    if request.len() > 16_000 { return Err("Desktop preview request limit: 16 KB".into()); }
    let output = app.shell().sidecar("prabha-engine")
        .map_err(|e| e.to_string())?
        .arg(request).output().await.map_err(|e| e.to_string())?;
    if !output.status.success() {
        return Err("The bundled simulation engine could not complete this request.".into());
    }
    serde_json::from_slice(&output.stdout).map_err(|e| format!("Invalid engine response: {e}"))
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![simulate])
        .run(tauri::generate_context!())
        .expect("Prabha could not start");
}
