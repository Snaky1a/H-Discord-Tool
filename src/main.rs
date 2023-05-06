mod features;

use features::get_info::check_token;
use features::utils::clear_console;
use std::io;
use std::process::exit;

#[tokio::main]
async fn main() -> () {
    clear_console();
    let mut option: String = String::new();
    println!(
        "Welcome to H-Discord-Tool!
╭─ Please, select an option ─╮
│ 1. Check token             │
│ 2. Placeholder             │
│ 3. Placeholder             │
│ 4. Placeholder             │
│ 5. Placeholder             │
│ 6. Placeholder             │
│ 7. Placeholder             │
│ 8. Placeholder             │
│ 9. Placeholder             │
│ 10. Exit                   │
╰────────────────────────────╯"
    );
    println!("Option [1/2/3/4/5/6/7/8/9/10]:");
    io::stdin().read_line(&mut option).expect("Err");
    let option: u32 = option.trim().parse().expect("Cannot fetch number");
    if option == 1 {
        let mut token: String = String::new();
        println!("Input token:");
        io::stdin().read_line(&mut token).expect("Err");
        check_token(&token).await;
    } else if option == 10 {
        exit(0)
    } else {
        println!("This is not a number!")
    }
}
