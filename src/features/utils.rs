use std::process::Command;

pub fn clear_console() {
    if cfg!(target_os = "windows") {
        Command::new("cmd")
            .args(["/c", "cls"])
            .spawn()
            .expect("bruh")
            .wait()
            .expect("failed to start");
    } else {
        Command::new("clear")
            .spawn()
            .expect("bruh")
            .wait()
            .expect("failed to start");
    };
}
