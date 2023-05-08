use chrono::{
    format::{DelayedFormat, StrftimeItems},
    DateTime, TimeZone, Utc,
};
use reqwest::{Client, Response};
use serde::Deserialize;
use std::{collections::HashMap, io::stdin, ops::Add};
use tokio::task;

#[derive(Debug, Deserialize)]
struct Me {
    id: String,
    username: String,
    global_name: Option<String>,
    display_name: Option<String>,
    avatar: Option<String>,
    discriminator: String,
    public_flags: i32,
    flags: i32,
    purchased_flags: i32,
    banner: Option<String>,
    banner_color: Option<String>,
    accent_color: Option<String>,
    bio: String,
    locale: String,
    nsfw_allowed: bool,
    mfa_enabled: bool,
    premium_type: i32,
    linked_users: Vec<String>,
    avatar_decoration: Option<String>,
    email: String,
    verified: bool,
    phone: Option<String>,
}

// #[derive(Debug, Deserialize)]
// struct Payments {
//     card_type: i16,
//     brand: String,
// }

fn check_flags(public_flags: i32) -> String {
    let flags: HashMap<i32, &str> = HashMap::from([
        (1 << 0, "Staff Team"),
        (1 << 1, "Guild Partner"),
        (1 << 2, "HypeSquad Events Member"),
        (1 << 3, "Bug Hunter Level 1"),
        (1 << 5, "Dismissed Nitro promotion"),
        (1 << 6, "House Bravery Member"),
        (1 << 7, "House Brilliance Member"),
        (1 << 8, "House Balance Member"),
        (1 << 9, "Early Nitro Supporter"),
        (1 << 10, "Team Supporter"),
        (1 << 14, "Bug Hunter Level 2"),
        (1 << 16, "Verified Bot"),
        (1 << 17, "Early Verified Bot Developer"),
        (1 << 18, "Moderator Programs Alumni"),
        (1 << 19, "Bot uses only http interactions"),
        (1 << 22, "Active Developer"),
    ]);
    let mut flags_list: Vec<&str> = Vec::new();

    for (key, value) in &flags {
        if (key & &public_flags) == *key {
            println!("true");
            flags_list.push(value);
        }
    }
    flags_list.join(", ")
}

async fn api_get(client: Client, url: &str, token: &str) -> Response {
    let resp = client
        .get(format!("https://discord.com/api/v10/{}", url))
        .header("authorization", token)
        .send()
        .await
        .expect("Error");
    resp
}

fn get_account_creation(snowflake_id: &u64) -> DateTime<Utc> {
    let user_creation = Utc
        .timestamp_millis_opt(((snowflake_id >> 22) + 1420070400000) as i64)
        .unwrap();
    user_creation
}

fn get_account_creation_and_convert(snowflake_id: &u64) -> DelayedFormat<StrftimeItems<'_>> {
    let user_creation = self::get_account_creation(snowflake_id).format("%d.%m.%Y %H:%M:%S");
    user_creation
}

async fn check_nitro_credit(token: &str) -> HashMap<&str, usize> {
    let client: Client = Client::new();
    let mut dict_credits: HashMap<&str, usize> = HashMap::new();

    let text = api_get(
        client,
        "users/@me/applications/521842831262875670/entitlements?exclude_consumed=true",
        token,
    )
    .await
    .text()
    .await;
    let text = text.unwrap();
    dict_credits.insert("Nitro Classic", text.matches("Nitro Classic").count());
    dict_credits.insert("Nitro Monthly", text.matches("Nitro Monthly").count());
    dict_credits.insert("Nitro Boost", text.matches("Nitro Boost").count());

    dict_credits
}

async fn get_guilds(token: &str) -> HashMap<String, Vec<String>> {
    let client: Client = Client::new();

    let mut guilds: HashMap<String, Vec<String>> = HashMap::new();

    let results = api_get(client, "users/@me/guilds?with_counts=true", token)
        .await
        .json::<serde_json::Value>()
        .await;

    for result in results.unwrap().as_array().unwrap() {
        let guild_id = result.get("id").unwrap();
        let guild_name = result.get("name").unwrap();
        let is_owner = result.get("owner").unwrap();

        guilds.insert(
            guild_id.to_string(),
            vec![guild_name.to_string(), is_owner.to_string()],
        );
    }

    guilds
}

pub async fn check_token(token: &str) {
    let token = token.trim();
    // let mut friend_type: HashMap<i32, &str> = HashMap::from([
    //     (1, "Friend"),
    //     (2, "Block"),
    //     (3, "incoming friend request"),
    //     (4, "outgoing friend request"),
    // ]);
    // let friend = friend_type.get(&5).unwrap_or(&"Unknown");

    let resp = self::api_get(Client::new(), "/users/@me", token).await;
    let nitro_credits = self::check_nitro_credit(token).await;

    if resp.status() == 200 {
        let text = resp.json::<Me>().await.unwrap();

        let pub_flags = self::check_flags(text.public_flags);

        let user_id = &text.id.parse::<u64>().unwrap();
        let user_creation = get_account_creation_and_convert(&user_id);

        println!(
            "{}",
            format!(
                "
Token {token} is valid

=== Account information ===
ID: {user_id}

name#tag: {username}
global name: {global_name}
display name: {display_name}

Bio: {bio}
Account locale: {locale}

Avatar URL: {avatar}
Avatar Decoration: {avatar_decoration}
Banner URL: {banner}
Banner Color: {banner_color}
Accent Color: {accent_color}

E-mail: {email}
E-mail is verified? {email_verified}
Phone number: {phone}
2FA enabled: {mfa}

NSFW allowed? {nsfw_allowed}

Created at: {created_at}

Premium type: {premium_type}
Public Flags: {public_flags}
Flags: {flags}
Purchased flags: {purchased_flags}
Linked users: {linked_users}
=======",
                token = token,
                user_id = text.id,
                username = String::from(text.username).add(&text.discriminator),
                global_name = text.global_name.unwrap_or("No global name".to_string()),
                display_name = text.display_name.unwrap_or("No display name".to_string()),
                bio = text.bio,
                locale = text.locale,
                avatar = text.avatar.unwrap_or("No avatar".to_string()),
                avatar_decoration = text
                    .avatar_decoration
                    .unwrap_or("No avatar decoration".to_string()),
                banner = text.banner.unwrap_or("No banner".to_string()),
                banner_color = text.banner_color.unwrap_or("No banner color".to_string()),
                accent_color = text.accent_color.unwrap_or("No accent color".to_string()),
                email = text.email,
                email_verified = text.verified,
                phone = text.phone.unwrap_or("No avatar".to_string()),
                mfa = text.mfa_enabled,
                nsfw_allowed = text.nsfw_allowed,
                created_at = user_creation,
                premium_type = text.premium_type,
                public_flags = pub_flags,
                flags = text.flags,
                purchased_flags = text.purchased_flags,
                linked_users = text.linked_users.join(", "),
            )
        );
        println!(
            "{}",
            format!(
                "
=== Nitro Credits ===
Nitro Classic credits: {classic}
Nitro Monthly credits: {monthly}
Nitro Boost credits: {boost}\n",
                classic = nitro_credits.get("Nitro Classic").unwrap(),
                monthly = nitro_credits.get("Nitro Monthly").unwrap(),
                boost = nitro_credits.get("Nitro Boost").unwrap(),
            )
        );

        println!("=== Guilds ===");

        for guild in get_guilds(&token).await {
            println!(
                "{}",
                format!(
                    "Guild id: {g_id}\nguild name: {g_name}\nIs owner? {g_is_owner}\n",
                    g_id = guild.0.replace("\"", ""),
                    g_name = guild.1.get(0).unwrap().replace("\"", ""),
                    g_is_owner = guild.1.get(1).unwrap().replace("\"", "")
                )
            );
        }
    } else {
        println!("token {} is not valid", token);
    }

    println!("Please any key to continue...");
    let mut temp = String::new();
    match stdin().read_line(&mut temp) {
        Ok(_) => task::spawn_blocking(|| {
            crate::main();
        })
        .await
        .expect("Task panicked"),
        Err(_) => {}
    }
}
