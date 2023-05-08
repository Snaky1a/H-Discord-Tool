mod features;

use features::get_info::check_token;
use features::utils::clear_console;
use std::io;
use std::process::exit;
use tokio::{
    task,
    time::{sleep, Duration},
};

#[tokio::main]
async fn main() -> () {
    clear_console();
    let mut temp: String = String::new();
    let mut option: i32 = 0;
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
    match io::stdin().read_line(&mut temp) {
        Ok(_) => match temp.trim().parse::<i32>() {
            Ok(_) => {
                option = temp.trim().parse::<i32>().unwrap();
            }
            Err(_) => {
                println!("This is not a number!");
                sleep(Duration::from_secs(3)).await;
                task::spawn_blocking(|| {
                    crate::main();
                })
                .await
                .expect("Task panicked");
            }
        },
        Err(_) => {
            println!("Try again");
            sleep(Duration::from_secs(3)).await;
            task::spawn_blocking(|| {
                crate::main();
            })
            .await
            .expect("Task panicked");
        }
    }

    if option == 1 {
        let mut token: String = String::new();
        println!("Input token:");
        io::stdin().read_line(&mut token).expect("Err");
        check_token(&token).await;
    } else if option == 10 {
        exit(0)
    } else {
        println!("This number isn't registered. Please, try again");
        sleep(Duration::from_secs(3)).await;
        task::spawn_blocking(|| {
            crate::main();
        })
        .await
        .expect("Task panicked");
    }
}
