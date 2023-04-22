from datetime import datetime
from typing import Union, Dict, Any, List, Tuple, Optional

import aiofiles
import aiohttp

from h_tool.helpers.logs import console
from ..helpers import menu

BASE_URL: str = "https://discord.com/"
friend_type: Dict[int, str] = {
    1: "Friend",
    2: "Block",
    3: "incoming friend request",
    4: "outgoing friend request"
}
flags: Dict[int, str] = {
    1 << 0: "Staff Team",
    1 << 1: "Guild Partner",
    1 << 2: "HypeSquad Events Member",
    1 << 3: "Bug Hunter Level 1",
    1 << 5: "Dismissed Nitro promotion",
    1 << 6: "House Bravery Member",
    1 << 7: "House Brilliance Member",
    1 << 8: "House Balance Member",
    1 << 9: "Early Nitro Supporter",
    1 << 10: "Team Supporter",
    1 << 14: "Bug Hunter Level 2",
    1 << 16: "Verified Bot",
    1 << 17: "Early Verified Bot Developer",
    1 << 18: "Moderator Programs Alumni",
    1 << 19: "Bot uses only http interactions",
    1 << 22: "Active Developer"
}


def from_datetime_to_humanly(
        date: datetime,
        to_string: Union[datetime.strptime, str] = "%d.%m.%Y %H:%M:%S"
) -> str:
    return date.strftime(to_string)


def get_user_flags(public_flags: int) -> List[str]:
    flags_all: List[str] = list()
    for key, value in flags.items():
        if (key and public_flags) == key:
            flags_all.append(value)

    return flags_all


def from_iso_format_to_humanly(
        iso: str,
        to_string: Union[datetime.strptime, str] = "%d.%m.%Y %H:%M:%S"
) -> str:
    date = datetime.fromisoformat(iso)
    return date.strftime(to_string)


def get_account_creation(snowflake_id: str, to_humanly: bool = True) -> Union[datetime, str]:
    user_creation = (int(snowflake_id) >> 22) + 1420070400000
    user_creation = datetime.fromtimestamp(user_creation / 1000.0)
    if to_humanly:
        user_creation = from_datetime_to_humanly(user_creation)
    return user_creation


async def check_nitro_credit(headers: Dict[Any, Any]) -> Tuple[int, int]:
    dict_credits = {"classic_credits": 0, "boost_credits": 0}
    async with aiohttp.ClientSession(
            base_url=BASE_URL,
            timeout=aiohttp.ClientTimeout(total=10)
    ) as session:
        async with session.get(
                "/api/v10/users/@me/applications/521842831262875"
                "670/entitlements?exclude_consumed=true",
                headers=headers
        ) as response:
            if response.status == 200:
                text = await response.text()
                dict_credits["classic_credits"] = text.count("Nitro Classic")
                dict_credits["boost_credits"] = text.count("Nitro Monthly")

    return dict_credits["classic_credits"], dict_credits["boost_credits"]


async def check_payments(headers: Dict[Any, Any]) -> Optional[Union[List[str], int]]:
    search_billing = None
    cc_digits = {"american express": "3", "visa": "4", "mastercard": "5"}
    account_cards, card = [], ""
    async with aiohttp.ClientSession(
            base_url=BASE_URL,
            timeout=aiohttp.ClientTimeout(total=10)
    ) as session:
        async with session.get(
                "/api/v10/users/@me/billing/payment-sources",
                headers=headers
        ) as response:
            if response.status == 200:
                search_billing = await response.json()
            elif (await response.json()).get("code") == 40002:
                return 403

    if search_billing:
        for grab in search_billing:
            grab1 = grab["billing_address"]
            if grab["type"] == 1:
                cc_brand = grab["brand"]
                cc_first = cc_digits.get(cc_brand)
                cc_last = grab["last_4"]
                cc_month = str(grab["expires_month"])
                cc_year = str(grab["expires_year"])
                card = f"""
    Payment Type: Credit card
    Valid: {not grab["invalid"]}
    CC Holder Name: {grab1["name"]}
    CC Brand: {cc_brand.title()}
    CC Number: {''.join(z if (i + 1) % 2 else f'{z} ' for i, z in
                        enumerate((cc_first if cc_first else '*')
                                  + ('*' * 11) + cc_last))}
    CC Date: {(f'0{cc_month}' if len(cc_month) < 2 else cc_month) + '/' + cc_year[2:4]}
    Address 1: {grab1["line_1"]}
    Address 2: {grab1["line_2"] if grab1["line_2"] else ''}
    City: {grab1["city"]}
    Postal code: {grab1["postal_code"]}
    State: {grab1["state"] if grab1["state"] else ''}
    Country: {grab1["country"]}
    Default Payment Method: {grab['default']}\n"""
            elif grab["type"] == 2:
                card = f"""
    Payment Type: PayPal
    Valid: {not grab['invalid']}
    PayPal Name: {grab1["name"]}
    PayPal Email: {grab['email']}
    Address 1: {grab1["line_1"]}
    Address 2: {grab1["line_2"] if grab1["line_2"] else ''}
    City: {grab1["city"]}
    Postal code: {grab1["postal_code"]}
    State: {grab1["state"] if grab1["state"] else ''}
    Country: {grab1["country"]}
    Default Payment Method: {grab['default']}\n"""
            account_cards.append(card)

    return account_cards


async def get_guilds(headers: Dict[Any, Any]) -> Dict[str, List[str]]:
    guilds: Dict[str, List[str]] = {}

    async with aiohttp.ClientSession(
            base_url=BASE_URL,
            timeout=aiohttp.ClientTimeout(total=10)
    ) as session:
        async with session.get(
                "/api/v9/users/@me/guilds?with_counts=true",
                headers=headers
        ) as response:
            if response.status == 200:
                r_json = await response.json()

                for guild in r_json:
                    guilds[guild["id"]] = [guild["name"], guild["owner"]]
    return guilds


async def get_gifts(headers: Dict[Any, Any]) -> List[str]:
    gifts = []

    async with aiohttp.ClientSession(
            base_url=BASE_URL,
            timeout=aiohttp.ClientTimeout(total=10)
    ) as session:
        async with session.get(
                "/api/v10/users/@me/entitlements/gifts",
                headers=headers
        ) as response:
            if response.status == 200:
                r_json = await response.json()

                for gift in r_json:
                    gifts.append(gift['subscription_plan']['name'])
    return gifts


async def get_me(headers: Dict[Any, Any]) -> Tuple[int, Any]:
    async with aiohttp.ClientSession(
            base_url=BASE_URL,
            timeout=aiohttp.ClientTimeout(total=10)
    ) as session:
        async with session.get(
                "/api/v10/users/@me",
                headers=headers
        ) as response:
            if response.status == 200:
                return response.status, await response.json()
            else:
                return response.status, ""


async def get_connections(headers: Dict[Any, Any]) -> Dict[Any, Any]:
    connections = {}
    async with aiohttp.ClientSession(
            base_url=BASE_URL,
            timeout=aiohttp.ClientTimeout(total=10)
    ) as session:
        async with session.get(
                "/api/v10/users/@me/connections",
                headers=headers
        ) as response:
            if response.status == 200:
                info = await response.json()

    for connection in info:
        connections[connection["type"]] = [
            connection["name"], connection["visibility"] == 1,
            connection["verified"], connection["revoked"]
        ]

    return connections


async def get_promotions(headers: Dict[Any, Any], locale: Optional[str] = None) -> Dict[Any, Any]:
    promo_ = {}
    res = None

    async with aiohttp.ClientSession(
            base_url=BASE_URL,
            timeout=aiohttp.ClientTimeout(total=10)
    ) as session:
        async with session.get(
                f"/api/v10/users/@me/outbound-promotions/codes?locale={locale if locale else 'us'}",
                headers=headers
        ) as response:
            if response.status == 200:
                res = await response.json()

    if res:
        for result in res:
            start_time = from_iso_format_to_humanly(result["promotion"]["start_date"])
            end_time = from_iso_format_to_humanly(result["promotion"]["end_date"])

            promo_[result["promotion"]["outbound_title"]] = [
                start_time, end_time,
                result["promotion"]["outbound_redemption_page_link"],
                result["code"]
            ]

    return promo_


async def check_boosts(headers: Dict[Any, Any]) -> Dict[Any, Any]:
    boosts = {}
    info = None

    async with aiohttp.ClientSession(
            base_url=BASE_URL,
            timeout=aiohttp.ClientTimeout(total=10)
    ) as session:
        async with session.get(
                "/api/v10/users/@me/guilds/premium/subscription-slots",
                headers=headers
        ) as response:
            if response.status == 200:
                info = await response.json()

    if info:
        for boost_info in info:
            boost_id = boost_info.get("id")
            guild_id, ended = "Unused boost", False
            subscription_id = boost_info["subscription_id"]
            if boost_info.get("premium_guild_subscription") is None:
                boost_status = "Unused (maybe cooldown)"
            else:
                guild_id = boost_info["premium_guild_subscription"]["guild_id"]
                ended = boost_info["premium_guild_subscription"]["ended"]
                boost_status = "Used"
            canceled = boost_info["canceled"]
            cooldown_ends_at = "No cooldown" \
                if boost_info["cooldown_ends_at"] is None \
                else from_iso_format_to_humanly(boost_info["cooldown_ends_at"])

            boosts[boost_id] = [
                guild_id, ended, boost_status,
                canceled, cooldown_ends_at, subscription_id
            ]

    return boosts


async def get_nitro_info(headers: Dict[Any, Any]) -> tuple[Union[str, None], Union[str, None]]:
    nitro_start, nitro_end = None, None

    async with aiohttp.ClientSession(
            base_url=BASE_URL,
            timeout=aiohttp.ClientTimeout(total=10)
    ) as session:
        async with session.get("/api/v10/users/@me/billing/subscriptions", headers=headers) as resp:
            if resp.status == 200:
                nitro_billing = await resp.json()

    if nitro_billing:
        nitro_start = from_iso_format_to_humanly(nitro_billing[0]["current_period_start"])
        nitro_end = from_iso_format_to_humanly(nitro_billing[0]["current_period_end"])

    return nitro_start, nitro_end


async def get_relationships(headers: Dict[Any, Any]) -> tuple[int, List[str]]:
    relationship_json, relationship_list = {}, []

    async with aiohttp.ClientSession(
            base_url=BASE_URL,
            timeout=aiohttp.ClientTimeout(total=10)
    ) as session:
        async with session.get("/api/v10/users/@me/relationships", headers=headers) as resp:
            relationship_json = await resp.json()

    if (relationship_json and
            not isinstance(relationship_json, list)
            and relationship_json.get("code") != 40002):
        for friend in relationship_json:
            user_flags = get_user_flags(friend['user']['public_flags'])
            user_id = friend["user"].get("id", 0)
            user_name = friend["user"].get("username")
            file_format = (
                'gif'
                if str(friend['user'].get('avatar', '')).startswith('a_')
                else 'png'
            )
            avatar = f"https://cdn.discordapp.com/avatars/{user_id}/{friend['user']['avatar']}." \
                     f"{file_format}" \
                if friend['user'].get("avatar") else None
            relationship_list.append(f"""\n
ID: {user_id}
Avatar URL: {avatar}
Account Creation: {get_account_creation(user_id)}
Nickname: {friend['nickname'] if friend['nickname'] is not None else user_name}
Name#tag: {f'{user_name}#{friend["user"]["discriminator"]}'}
Friend type: {friend_type.get(friend['type'], 'Unknown')}
Flags: {', '.join(user_flags) if user_flags else 'No flags'}""")

    return len(relationship_list), relationship_list


async def get_dms(headers: Dict[Any, Any]) -> List[str]:
    dms_json, direct_messages = {}, []

    async with aiohttp.ClientSession(
            base_url=BASE_URL,
            timeout=aiohttp.ClientTimeout(total=10)
    ) as session:
        async with session.get("/api/v10/users/@me/channels", headers=headers) as resp:
            if resp.status == 200:
                dms_json = await resp.json()

    if dms_json:
        for i, dm in enumerate(dms_json):
            text = f"\nPrivate channel №{i + 1}\nID: {dm['id']}\n" \
                   f"Friend type: {friend_type.get(dm.get('type', 0), 'Unknown')}" \
                   f"\nLast message id: {dm.get('last_message_id', None)}\n" \
                   f"Channel created at: {get_account_creation(dm['id'])}\n\nRecipients:\n"
            for recipient in dm['recipients']:
                user_flags = get_user_flags(recipient.get("public_flags", 0))
                user_id = recipient["id"]
                user_name = recipient["username"]
                discriminator = recipient["discriminator"]
                avatar = (
                    f"https://cdn.discordapp.com/avatars/{user_id}/{recipient.get('avatar', '')}.",
                    f"{'gif' if str(recipient.get('avatar', '')).startswith('a_') else 'png'}"
                    if recipient.get("avatar", None)
                    else None
                )
                text += f"ID: {user_id}\n" \
                        f"Name#Tag: {f'{user_name}#{discriminator}'}\n" \
                        f"Avatar URL: {avatar}\n" \
                        f"Account Creation: {get_account_creation(user_id)}\n" \
                        f"Global Name: {recipient.get('global_name', user_name)}\n" \
                        f"Display Name: {recipient.get('display_name', user_name)}\n" \
                        f"Bot: {recipient.get('bot', False)}\n" \
                        f"Flags: {', '.join(user_flags) if user_flags else 'No flags'}\n\n"
            direct_messages.append(text)

    return direct_messages


async def check_token(token: str, mask_token: bool = True) -> None:
    headers = {
        "Accept": "*/*",
        "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
        "Alt-Used": "discord.com",
        "Authorization": token,
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Cookie": "__dcfduid=8ae3ca90b4d911ec998447df76ccab6d; "
                  "__sdcfduid"
                  "=8ae3ca91b4d911ec998447df76ccab6d07a29d8ce7d96383bcbf0ff"
                  "12d2f61052dd1691af72d9101442df895f59aa340; "
                  "OptanonConsent=isIABGlobal=false&datestamp=Tue+Sep+20+2"
                  "022+15%3A55%3A24+GMT%2B0200+("
                  "hora+de+verano+de+Europa+central)&version=6.33.0&hosts="
                  "&landingPath=NotLandingPage&groups=C0001"
                  "%3A1%2CC0002%3A1%2CC0003%3A1&AwaitingReconsent=false&geolocation=ES%3BMD; "
                  "__stripe_mid=1798dff8-2674-4521-a787-81918eb7db2006dc53; "
                  "OptanonAlertBoxClosed=2022-04-15T16:00:46.081Z; _ga=GA1.2.313716522.1650038446; "
                  "_gcl_au=1.1.1755047829.1662931666; _gid=GA1.2.778764533"
                  ".1663618168; locale=es-ES; "
                  "__cfruid=fa5768ee3134221f82348c02f7ffe0ae3544848a-1663682124",
        "Host": "discord.com",
        "Origin": "https://discord.com",
        "Referer": "https://discord.com/app",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0)"
                      " Gecko/20100101 Firefox/105.0",
    }
    if mask_token:
        temp = token.split(".")[-1]
        masked_token = temp.replace(temp, "*" * len(temp))
        masked_token = f"{'.'.join(token.split('.')[:-1])}.{masked_token}"
    else:
        masked_token = token

    status, info = await get_me(headers=headers)

    if status == 200:
        locale = None
        nitro_start, nitro_end = "No nitro", "No nitro"

        user_creation = get_account_creation(info["id"])
        guilds_text, payments_text, \
            gifts_text, promotions_text, connections_text, \
            boosts_text, rel_text, private_channels_text = "=== Guilds ===\n", \
            "=== Payments ===\n", "=== Gifts info ===\n", \
            "=== Promotions ===\n", "=== Account connections ===\n", \
            "=== Boosts ===\n", "=== Relationships ===\n", \
            "=== Private channels ===\n"
        if "locale" in info:
            locale = info["locale"]

        flags_all = get_user_flags(info["public_flags"])

        premium_type = "No nitro" \
            if info["premium_type"] == 0 \
            else "Nitro Classic" \
            if info["premium_type"] == 1 \
            else "Nitro Boost" if info["premium_type"] == 2 else "Nitro Basic"

        if premium_type != "No nitro":
            nitro_start, nitro_end = await get_nitro_info(headers=headers)

        classic_credits, nitro_boost_credits = await check_nitro_credit(headers=headers)
        nitro_credits = f"Nitro classic/boost credits: {classic_credits}/{nitro_boost_credits}"

        # "You need to verify your account in order to perform this action." check
        if (payments := await check_payments(headers=headers)) != 403:
            payments_text += ''.join(
                [f'{payment}\n' for payment in payments]
            ) if len(payments) >= 1 else "No payments in account"
        else:
            console.print(f"token {masked_token} is phone locked!")
            return

        gifts = await get_gifts(headers=headers)
        gifts_text += "".join(
            [f'{gift}\n' for gift in gifts]
        ) if len(gifts) >= 1 else 'No gifts in account'

        count, relationships = await get_relationships(headers=headers)
        rel_text += f"Total relationships: {count}"
        rel_text += ''.join([text for text in relationships])

        guilds = await get_guilds(headers=headers)
        guilds_text += ''.join(
            [
                f"ID: {_id} | Name: {name} | Owner: {owner}\n"
                for _id, (name, owner) in guilds.items()
            ]
        ) if len(guilds) >= 1 else "No guilds in account"

        connections = await get_connections(headers=headers)
        connections_text += ''.join([
            f"Connection type: {conn_type} | Nickname: {name} | shows in profile: {sh_prof} |"
            f" Verified?: {verified} | Revoked: {revoked}\n"
            for conn_type, (name, sh_prof, verified, revoked) in connections.items()
        ]) if len(connections) >= 1 else "No connections in account"

        promotions = await get_promotions(headers=headers, locale=locale or "en")
        promotions_text += ''.join([
            f"Promo: {name} | Start time: {s_time} | End time: {end_time} |"
            f" Link to activate: {link} | Code: {code}\n"
            for name, (s_time, end_time, link, code) in promotions.items()
        ]) if len(promotions) >= 1 else "No promotions in account"

        boosts = await check_boosts(headers=headers)
        boosts_text += ''.join([
            f"Boost status: {boost_status} | Guild id: {guild_id} | Boost id: {boost_id} "
            f"| ended: {ended} | canceled: {canceled} | Cooldown ends: {cooldown_end}\n"
            for boost_id, (
                guild_id,
                ended, boost_status, canceled,
                cooldown_end, subscription_id
            ) in boosts.items()
        ]) if len(boosts) >= 1 else "No boosts in account"

        direct_messages = await get_dms(headers=headers)
        private_channels_text += f"Total private channels: {len(direct_messages)}\n"
        private_channels_text += ''.join([text for text in direct_messages])

        username = info.get("username")
        full_name = f"{info.get('username')}#{info.get('discriminator')}"
        avatar_format = (
            'gif'
            if str(info.get('avatar', '')).startswith('a_')
            else 'png'
        )
        banner_format = (
            'gif'
            if str(info.get('banner', '')).startswith('a_')
            else 'png'
        )
        avatar = f"https://cdn.discordapp.com/avatars/{info.get('id')}/{info.get('avatar')}." \
                 f"{avatar_format}" if info.get("avatar") else None
        banner = f"https://cdn.discordapp.com/banners/{info.get('id')}/{info.get('banner')}." \
                 f"{banner_format}" if info.get("banner") else None
        email = info.get("email")
        phone = info.get("phone")
        verified = info.get("verified", False)
        mfa = info.get("mfa_enabled", False)
        bio = info.get("bio")
        user_id = info["id"]

        full_text = f"""
Token {masked_token} is valid

=== Account information ===
ID: {user_id}
name#tag: {username}
Full name: {full_name}
Bio: {bio}
Account locale: {locale if locale else 'cannot fetch account locale'}
Avatar URL: {avatar}
Banner URL: {banner}
E-mail: {email}
E-mail is verified? {verified}
Phone number: {phone}
2FA enabled: {mfa}
Created at: {user_creation}
Public Flags: {', '.join(flags_all) if flags_all else 'No flags'}
=======

=== Nitro information ===
Nitro: {premium_type}
Nitro started: {nitro_start}
Nitro ends: {nitro_end}
{nitro_credits}
=======

{payments_text}
=======

{guilds_text}
=======

{gifts_text}
=======

{promotions_text}
=======

{connections_text}
=======

{boosts_text}
=======

{rel_text}
=======

{private_channels_text}
======="""

        async with aiofiles.open("h_tool/saved/token_info.txt", "w", encoding="utf-8") as f:
            await f.write(full_text)

        minimal_text = f"""
=== Account Information ===
Token: {token}
ID: {user_id}
name#tag: {username}
Account locale: {locale if locale else 'cannot fetch account locale'}
Created at: {user_creation}
Public Flags: {', '.join(flags_all) if flags_all else 'No flags'}

=== Security ===
2FA:        {mfa}
E-mail:     {email}
E-mail is verified?     {verified}
Phone number:   {phone}

=== Nitro information ===
Nitro: {premium_type}
Nitro started: {nitro_start}
Nitro ends: {nitro_end}
Nitro classic/boost credits: {classic_credits}/{nitro_boost_credits}

Full information about this token saved in h_tool/saved/token_info.txt
                """
        console.print(minimal_text)
    elif status == 401:
        console.print(f"token {masked_token} invalid!")
    elif status == 403:
        console.print(f"token {masked_token} is phone locked!")
    elif status == 429:
        console.print("Rate Limit")
    await menu.main_menu()
