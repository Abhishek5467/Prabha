#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
use serde_json::Value;
use tauri_plugin_dialog::DialogExt;
use tauri_plugin_opener::OpenerExt;
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

#[tauri::command]
async fn save_export(app: tauri::AppHandle, name: String, bytes: Vec<u8>) -> Result<bool, String> {
    if bytes.len() > 16 * 1024 * 1024 {
        return Err("Desktop exports are limited to 16 MB.".into());
    }
    // The caller supplies a suggested basename, never a filesystem destination.
    if name.is_empty() || name.len() > 160 ||
        !name.chars().all(|c| c.is_ascii_alphanumeric() || "._-".contains(c)) {
        return Err("Invalid export filename.".into());
    }
    let extension = name.rsplit('.').next().unwrap_or("").to_lowercase();
    if !["json", "csv", "png", "zip", "prabha"].contains(&extension.as_str()) {
        return Err("Unsupported export file type.".into());
    }
    // Blocking dialogs must run off the main event loop.
    tauri::async_runtime::spawn_blocking(move || {
        let chosen = app.dialog().file().set_title("Export from Prabha")
            .set_file_name(&name).add_filter("Prabha export", &[extension.as_str()])
            .blocking_save_file();
        let Some(chosen) = chosen else { return Ok(false); };
        let path = chosen.into_path().map_err(|e| e.to_string())?;
        std::fs::write(path, bytes).map_err(|e| format!("Could not save export: {e}"))?;
        Ok(true)
    }).await.map_err(|e| e.to_string())?
}

#[tauri::command]
fn open_external(app: tauri::AppHandle, url: String) -> Result<(), String> {
    let parsed = tauri::Url::parse(&url).map_err(|e| e.to_string())?;
    if parsed.scheme() != "https" || !parsed.username().is_empty() || parsed.password().is_some() {
        return Err("External links must use HTTPS without credentials.".into());
    }
    app.opener().open_url(parsed.as_str(), None::<&str>).map_err(|e| e.to_string())
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![simulate, save_export, open_external])
        .run(tauri::generate_context!())
        .expect("Prabha could not start");
}
