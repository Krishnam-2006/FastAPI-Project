import asyncio
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
from sqlalchemy import delete, select, update

import models
from database import AsyncSessionLocal, engine
from image_utils import PROFILE_PICS_DIR
from main import app

import selectors

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

POPULATE_IMAGES_DIR = Path("populate_images")

USERS = [
    {
        "username": "YoriichTsugikuni",
        "email": "yoriichi.tsugikuni@demonslayer.com",
        "password": "TestPassword1!",
        "image": "Yoriichi Tsugikuni.jpg",
    },
    {
        "username": "TanjiroKamado",
        "email": "tanjiro.kamado@demonslayer.com",
        "password": "TestPassword2!",
        "image": "tanjiro1.jpg",
    },
    {
        "username": "MuzanKibutsuji",
        "email": "muzan.kibutsuji@demonslayer.com",
        "password": "TestPassword3!",
        "image": "muzan1.jpg",
    },
    {
        "username": "Akaza",
        "email": "akaza@demonslayer.com",
        "password": "TestPassword4!",
        "image": "akaza1.jpg",
    },
    {
        "username": "Kokushibo",
        "email": "kokushibo@demonslayer.com",
        "password": "TestPassword5!",
        "image": "Kokushibo.jpg",
    },
]

POSTS = [
    # [0] => Muzan
    {
        "title": "A Thousand Years and Still No Equal",
        "content": "I have existed for a thousand years. In that time, I have faced armies, Demon Slayer Corps generation after generation, and not one has come close to ending me. They sharpen their blades, train their breathing, and still they fall. I do not hate them. I simply find them... insufficient. The only one who ever gave me pause was Yoriichi — and even he failed. I remain. That is simply the truth.",
    },
    # [1] => Tanjiro
    {
        "title": "How I Survived Mt. Sagiri: The Final Selection",
        "content": "The Final Selection on Mt. Sagiri was the hardest week of my life. Surrounded by demons and armed only with a Nichirin blade, every sunrise felt like a miracle. I made it through by remembering my family — especially Nezuko. Every swing of my sword carries their memory. If you're reading this and considering the path of a Demon Slayer, know that it is not glory that carries you. It is love.",
    },
    # [2] => Yoriichi
    {
        "title": "On the Origin of Sun Breathing",
        "content": "I did not create Sun Breathing out of ambition. It came naturally — the way a river finds the sea. When I first picked up a sword, the movements simply made sense to me. What others called genius, I called breathing. I only hope that what I've left behind is enough. The world deserved better than my failure against Muzan.",
    },
    # [3] => Kokushibo
    {
        "title": "Moon Breathing: Forged in the Shadow of a Brother",
        "content": "I developed Moon Breathing because Sun Breathing was never mine to have. My brother Yoriichi was born with a gift I could not replicate, no matter how hard I trained. So I built something new — sixteen forms that cut through space itself, crescent waves of blood and steel. It is mine. It has always been mine. And yet... standing over him as he died, blade in hand, I understood I had never surpassed him at all.",
    },
    # [4] => Akaza
    {
        "title": "Strength Is the Only Truth That Doesn't Lie",
        "content": "Everything in this world decays. Ideals, empires, love — all of it rots. But strength? Strength is honest. You are either strong enough or you are not. I have devoted centuries to becoming something no human or demon can match. Every scar I've taken was a lesson. Every opponent I've shattered was a step forward. This is not cruelty. This is discipline.",
    },
    # [5] => Muzan
    {
        "title": "Why I Fear the Sun — And Why I Will Conquer It",
        "content": "Sunlight is the one thing I cannot overcome. It is an insult I have carried for a millennium. Every demon I create, every Upper Moon I strengthen — it is all in service of one goal: a demon who can walk in daylight. I came close with Nezuko Kamado. I will not stop. The sun will not define my limits forever.",
    },
    # [6] => Tanjiro
    {
        "title": "What Rengoku Taught Me in His Final Moments",
        "content": "Rengoku Kyojuro died on the Mugen Train, and I was powerless to stop it. But before he went, he looked at me and said to set my heart ablaze. I didn't fully understand it then. Now I do. He didn't mean anger. He meant conviction — the kind that burns clean, without hatred, without hesitation. I carry his flame now. I won't let it go out.",
    },
    # [7] => Yoriichi
    {
        "title": "The Day I Faced Muzan",
        "content": "I found him alone one night. A thousand years of demon plague — and there he was. I drew my sword and moved through the Thirteenth Form. He should have died. Every vital organ, every regenerative pathway — I targeted them all. But he scattered. Pieces of him fled into the dark. I sat down beneath a tree that night and wept. Not from sadness. From the weight of knowing I had come so close, and the world would continue to suffer.",
    },
    # [8] => Kokushibo
    {
        "title": "On the Upper Moon Hierarchy",
        "content": "As Upper Moon One, I sit at the apex of Lord Muzan's Twelve Kizuki. Below me: Doma, Akaza, Hantengu, Gyokko, and the others. Each is powerful in their own right. Akaza's combat instincts are impressive — I will grant him that. But there is a ceiling he does not yet see. I have stood at the top of this hierarchy for centuries. The view is colder than most imagine.",
    },
    # [9] => Akaza
    {
        "title": "Rengoku Was the Best Fight of My Existence",
        "content": "I have fought thousands. Warriors, demons, Hashira — I have ended them all. But Kyojuro Rengoku was different. He knew he was losing and he did not flinch. He did not beg. He kept his flame burning until there was nothing left to burn. I offered him demonhood because I genuinely did not want to see that fire go out. He refused. And he was right to. I still think about that fight.",
    },
    # [10] => Muzan
    {
        "title": "The Twelve Kizuki: Tools, Not Allies",
        "content": "People think I feel loyalty to my Twelve Kizuki. I do not. They are instruments — finely crafted, yes, but instruments nonetheless. When a Lower Moon fails, I replace them. When an Upper Moon disappoints, I eliminate them in front of the rest as a lesson. Kokushibo is useful. Akaza is effective. But none of them are irreplaceable. Only I am irreplaceable.",
    },
    # [11] => Tanjiro
    {
        "title": "Water Breathing: The Style That Carried Me This Far",
        "content": "Sakonji Urokodaki taught me Water Breathing, and it has saved my life more times than I can count. The ten forms flow into each other like a river — each one adapting to the situation. It's not the most powerful style, but it's the most honest. You work with what's around you. You don't force the fight. You find the current and follow it.",
    },
    # [12] => Yoriichi
    {
        "title": "To My Brother, Whom I Could Not Save",
        "content": "Michikatsu. I never blamed you for the path you chose. I understood, even then, that my ability came with a kind of cruelty — not intentional, but real. To walk beside a brother who makes everything look effortless while you bleed for every step... I should have said more. I should have told you that your effort was worth more than my talent. I am sorry, Michikatsu. I am sorry I did not say it sooner.",
    },
    # [13] => Kokushibo
    {
        "title": "What It Means to Abandon Humanity",
        "content": "When I became a demon, I told myself it was a means to an end — more time, more power, the chance to surpass Yoriichi. I did not expect to lose myself so completely. Centuries passed. My human memories became distant, then strange, then almost unrecognizable. In my final battle, they came back all at once. That is the cruelest irony of demonhood: you sacrifice your humanity to gain power, and only at the very end do you remember what you gave away.",
    },
    # [14] => Akaza
    {
        "title": "Destructive Death: Compass Needle Explained",
        "content": "Compass Needle is not a single technique — it is a system. Every strike is calculated to detect and target the precise center of an opponent's force. The moment you commit to a movement, I have already mapped the counter. I developed this over centuries of combat. It is not magic. It is pattern recognition, pushed beyond what any human mind can sustain without demonic enhancement.",
    },
    # [15] => Muzan
    {
        "title": "On the Concept of Fear",
        "content": "Humans say I rule through fear. They are not wrong. But what they do not understand is that fear is simply clarity — the accurate recognition of power. When my subordinates tremble in my presence, they are being rational. The ones who don't fear me are the ones who don't understand the situation. Yoriichi was the only one who stood before me without fear, and he nearly killed me. So yes. Fear me. It is the correct response.",
    },
    # [16] => Tanjiro
    {
        "title": "My Friends Are My Strength — And My Weakness",
        "content": "People sometimes ask how I keep going after everything I've seen. The answer is Inosuke, Zenitsu, Nezuko. My friends. Every time I think about giving up, I remember that they're fighting too — and that they need me at my best. That might sound simple, but simple things are often the truest. I don't fight to be the strongest. I fight because the people I love deserve a safer world.",
    },
    # [17] => Yoriichi
    {
        "title": "The Thirteenth Form Was Never Meant to Be a Secret",
        "content": "I never hid Sun Breathing's Thirteenth Form. I simply could not teach it — not because I was selfish, but because it could not be learned through instruction. It had to be felt. It is a loop of all twelve forms, seamless and unending, each one feeding into the next. The only way to reach it is to know the first twelve so deeply they become instinct. Then, in the right moment, the Thirteenth reveals itself.",
    },
    # [18] => Kokushibo
    {
        "title": "The Demon Slayer Mark: A Warning I Recognized Too Late",
        "content": "I bore the Demon Slayer Mark when I was human. I was told it was a death sentence — that those marked would not survive past age 25. That fear drove my decision to become a demon. What I understand now, too late, is that Yoriichi bore the same mark and lived past seventy, still wielding a blade sharp enough to nearly destroy Muzan. The mark was not the problem. My cowardice was.",
    },
    # [19] => Akaza
    {
        "title": "Why I Refuse to Fight Women",
        "content": "I have never raised my hand against a woman in my entire existence — human or demon. This is not weakness. It is a principle I formed long before I became Upper Moon Three, rooted in a life I no longer fully remember but cannot fully forget either. Some boundaries are not negotiable, regardless of who or what I have become. Doma finds this amusing. He is welcome to.",
    },
    # [20] => Muzan
    {
        "title": "Tamayo Was a Mistake I Should Have Corrected Sooner",
        "content": "Lady Tamayo. A demon I created centuries ago who had the audacity to break free of my control and spend her existence working against me. She developed medicine. She collaborated with the Demon Slayer Corps. And in the end, her research was a key component of my defeat. I underestimated her. It is perhaps the only time I have made that mistake. I do not make it twice — but once was enough.",
    },
    # [21] => Tanjiro
    {
        "title": "The Swordsmith Village and Haganezuka's Dedication",
        "content": "Haganezuka is terrifying. Not in the way demons are terrifying — in the way that someone who cares about their craft more than anything else in the world is terrifying. He chased me through a forest in a mask just because I damaged his blade. And yet, that blade has saved my life more times than any strategy or breathing technique. Respect your swordsmith. They are your lifeline.",
    },
    # [22] => Yoriichi
    {
        "title": "Breathing Is Not a Technique. It Is a State of Being.",
        "content": "When people call Sun Breathing a 'style', I understand what they mean, but they are slightly wrong. Breathing is not a set of moves you memorize. It is a relationship between your body, your mind, and the world around you. You do not perform it. You inhabit it. The forms exist to give beginners structure. The goal is to eventually transcend the forms entirely — to breathe as naturally as the lungs do.",
    },
    # [23] => Kokushibo
    {
        "title": "Centuries of Combat: What Changes and What Doesn't",
        "content": "After four hundred years of fighting, I expected the experience to become routine. It has not. Every serious opponent reveals something new — a variation in technique, a timing I had not considered, a will that burns in a direction I didn't anticipate. Gyomei Himejima, the Stone Hashira, came closer to giving me a real fight than anyone in over a century. That surprised me. I respect surprises.",
    },
    # [24] => Akaza
    {
        "title": "On the Memory of a Life I Can't Quite Reach",
        "content": "There are flashes. A woman's smile. The smell of medicine. A promise I made to someone I loved. I don't know why these images come to me. Demons don't dream, and yet something in me reaches backward. I've learned not to fight it. Whatever that life was — whoever I was — it was part of what made me. Even if I can no longer see it clearly, I can feel its outline.",
    },
    # [25] => Muzan
    {
        "title": "Nezuko Kamado: The Variable I Did Not Account For",
        "content": "I have turned thousands of humans into demons. Every one of them follows a predictable curve — bloodlust, power growth, hierarchy. Nezuko did not. She suppressed her hunger. She fought alongside humans. She developed a Blood Demon Art of genuine power. And then she walked in sunlight. No demon had ever done that. I needed that ability. I needed her. The fact that she ended up on the wrong side of this war is a miscalculation I find... unacceptable.",
    },
    # [26] => Tanjiro
    {
        "title": "Zenitsu Is Braver Than He Thinks",
        "content": "Zenitsu Agatsuma complains constantly. He cries at the start of most missions. He insists he's going to die. And then — every single time — when it counts, he moves faster than anyone I've ever seen. I think his fear isn't cowardice. I think it's honesty. He knows exactly how dangerous the situation is, and he chooses to act anyway. That's not weakness. That's the definition of courage.",
    },
    # [27] => Yoriichi
    {
        "title": "The Sun Is Not My Weapon. It Is My Teacher.",
        "content": "People see Sun Breathing and think of fire and power. But sunlight is patient. It rises the same way every morning regardless of what happened the night before. It does not rush. It does not compensate. It simply arrives, fully itself, and illuminates everything. That is what I have tried to embody — not blazing destruction, but consistent, complete presence. The sun does not try to be the sun. It simply is.",
    },
    # [28] => Kokushibo
    {
        "title": "The Nichirin Blade That Turned Red",
        "content": "In my final battle, Sanemi Shinazugawa's blade turned red — the first time I had seen a Nichirin blade truly ignite with that power in centuries. It inhibited my regeneration in a way I had not experienced. I found it... fascinating, even as it was being used to destroy me. A warrior who can push a blade to that state in the heat of combat is exceptional. I acknowledged it then. I acknowledge it now.",
    },
    # [29] => Akaza
    {
        "title": "Upper Moon Two: My Thoughts on Doma",
        "content": "Doma sits above me in the hierarchy, and I despise it. Not because he isn't powerful — he is — but because he feels nothing. He kills without satisfaction, wins without meaning, exists without purpose. Power is only worth having if it means something to you. Doma's strength is hollow. Mine was built from something real, even if I can't fully remember what that something was anymore.",
    },
    # [30] => Muzan
    {
        "title": "The Ubuyashiki Bloodline: A Thorn Across Generations",
        "content": "For a thousand years, the Ubuyashiki family has led the Demon Slayer Corps against me. Each generation, a new face with the same name and the same curse — a fragile body that barely lasts past middle age. And yet they kept coming. Kagaya Ubuyashiki was the last, and he chose to die in a way that wounded me. I will admit, in the privacy of this moment, that I underestimated the damage a dying man could do.",
    },
    # [31] => Tanjiro
    {
        "title": "Inosuke Taught Me That There's More Than One Way to Be Strong",
        "content": "Inosuke Hashibira grew up in the mountains, raised by boars, with no formal training and no breathing teacher. He invented his own style entirely from instinct. And it works — beautifully and terrifyingly. Watching him fight taught me that strength doesn't come from a single mold. Beast Breathing is chaotic, unpredictable, and completely his. I think there's something important in that.",
    },
    # [32] => Yoriichi
    {
        "title": "I Was Not Born a Prodigy. I Was Born Paying Attention.",
        "content": "Everyone calls what I had a gift. Perhaps it was. But I also spent every waking hour watching — how water moves, how fire burns, how animals breathe when they run. I was not performing techniques. I was listening to the world and learning to move like it does. The sword was simply the instrument through which I expressed what I already understood. I was not special. I was attentive.",
    },
    # [33] => Kokushibo
    {
        "title": "What I See When I Fight",
        "content": "When I enter combat, I do not see a person. I see vectors — lines of force, angles of attack, the geometry of movement. Four centuries of fighting have reduced it to something almost mathematical. But in my final moments against the Hashira, something shifted. The geometry faded, and I saw people. Real ones. It was the most disoriented I have ever felt in battle. I am still not sure if it was a weakness or a clarity.",
    },
    # [34] => Akaza
    {
        "title": "The Moment I Remembered",
        "content": "It came back to me all at once. Her name. Her face. The dojo. The promise I made. Koyuki. I had buried it so deep beneath centuries of combat and demonic transformation that I believed it was gone. But when Tanjiro refused to let me end his life — when he looked at me without hatred — something cracked open. I remembered who I was before all of this. And I chose, in the end, to be him again.",
    },
    # [35] => Muzan
    {
        "title": "On Adaptability: Why I Have Survived This Long",
        "content": "I have survived a thousand years not because I am the strongest combatant in any given moment — though I am — but because I adapt. I change shape. I change strategy. I change location, appearance, identity. The Demon Slayer Corps has tried to corner me repeatedly. They cannot, because I am not a fixed target. I am a variable. And variables do not get caught.",
    },
    # [36] => Tanjiro
    {
        "title": "The Hinokami Kagura: A Dance Becomes a Sword",
        "content": "My father danced the Hinokami Kagura every New Year, from midnight until dawn, in the freezing cold. He never told us what it meant — only that we had to protect it and pass it on. When I used it in battle for the first time, I felt him beside me. I didn't know then that it was Sun Breathing. I only knew that it felt like him. Like home. Like something worth protecting.",
    },
    # [37] => Yoriichi
    {
        "title": "The Weight of a Mark",
        "content": "The Demon Slayer Mark appeared on me early. I was told what it meant — that I would likely not survive past twenty-five. I accepted it. I was not afraid of death; I was afraid of leaving the world worse than I found it. As it turned out, I lived far longer than the mark was supposed to allow. I do not know why. Perhaps the mark is not a death sentence. Perhaps it is simply a measure of how hard someone is willing to push before they let go.",
    },
    # [38] => Kokushibo
    {
        "title": "Four Hundred Years of Moon Breathing",
        "content": "In four hundred years, I have refined Moon Breathing to something that barely resembles what I first created as a human demon slayer. The crescent projections now move at speeds that make them invisible in darkness. The sixteenth form can sever a Hashira-level opponent in a single sustained movement if they are even slightly out of position. I am proud of this. It is the one thing I built entirely by myself, for myself.",
    },
    # [39] => Akaza
    {
        "title": "To Any Fighter Who Ever Pushed Me to My Limit",
        "content": "There have been four of you across three centuries. You know who you are — or you would, if you were still alive. Each of you forced me to reach deeper than I knew I could. Each of you made me better. I do not mourn you the way humans mourn. But I carry you in a different way — in the refinements I made the day after we fought, in the gaps in my technique that you exposed and forced me to close. That is my version of remembrance.",
    },
    # [40] => Muzan
    {
        "title": "The Final Night: What I Did Not Expect",
        "content": "I did not expect the Corps to storm the Infinity Castle the way they did. Coordinated. Simultaneous. Kamado in one corridor, the Hashira distributed across the structure, Tamayo's drug already in my bloodstream before I realized it. I was forced to acknowledge, in those hours, that I had been outplanned. Not outpowered — outplanned. That is a distinction that matters. I still have not fully processed it.",
    },
    # [41] => Tanjiro
    {
        "title": "What I Want for Nezuko",
        "content": "I don't want Nezuko to fight forever. I don't want her to have to carry a sword or face demons or wake up wondering if today is the day she loses herself. I want her to walk in sunlight — which she can now. I want her to laugh the way she used to before that night. I want her to be a person, not a symbol. She has already been so brave. She deserves to just be my sister.",
    },
    # [42] => Yoriichi
    {
        "title": "A Note to Whoever Comes After Me",
        "content": "If you are reading this and you carry a sword in the dark, know that you are not alone — not really. Every person who has ever done this before you is still here, in some form. In the techniques passed down, in the courage that seems to appear from nowhere when you need it most, in the sunrise you're fighting to protect. I will not tell you it gets easier. But I will tell you it is worth it. It has always been worth it.",
    },
]

POST_44 = {
    "title": "Fun Fact: Yoriichi Never Lost a Single Duel",
    "content": "If you've paginated all the way to this post, the 44th one, you've earned a secret: in his entire life as a Demon Slayer, Yoriichi Tsugikuni was never defeated in a duel against a demon or a human. The only time he 'failed' was when Muzan escaped — and even then, Muzan fled missing several of his organs. No swordsman in history has come closer to ending it all in a single encounter.",
}


async def clear_existing_data() -> None:
    # Delete profile pictures from local storage
    if PROFILE_PICS_DIR.exists():
        for file in PROFILE_PICS_DIR.iterdir():
            if file.is_file() and file.name != ".gitkeep":
                file.unlink()
        print(f"Deleted profile pictures from {PROFILE_PICS_DIR}")

    # Clear database tables (order respects foreign keys)
    async with AsyncSessionLocal() as db:
        await db.execute(delete(models.PasswordResetToken))
        await db.execute(delete(models.Post))
        await db.execute(delete(models.User))
        await db.commit()
    print("Cleared existing data")


async def update_post_dates() -> None:
    now = datetime.now(UTC)

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(models.Post).order_by(models.Post.id))
        posts = result.scalars().all()

        if not posts:
            return

        # First post (POST_44) is the oldest - ~90 days ago
        await db.execute(
            update(models.Post)
            .where(models.Post.id == posts[0].id)
            .values(date_posted=now - timedelta(days=90)),
        )

        # Remaining posts: each ~1.5 days newer than previous
        for i, post in enumerate(posts[1:], start=1):
            days_ago = (len(posts) - i) * 1.5
            hours_offset = (i * 7) % 24
            post_date = now - timedelta(days=days_ago, hours=hours_offset)
            await db.execute(
                update(models.Post)
                .where(models.Post.id == post.id)
                .values(date_posted=post_date),
            )

        await db.commit()
    print("Updated post dates")


async def populate() -> None:
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://localhost",
    ) as client:
        # Clear existing data (local images first, then database)
        await clear_existing_data()

        users: list[dict] = []

        print(f"\nCreating {len(USERS)} users...")
        for user_data in USERS:
            response = await client.post(
                "/api/users",
                json={
                    "username": user_data["username"],
                    "email": user_data["email"],
                    "password": user_data["password"],
                },
            )
            response.raise_for_status()
            user = response.json()
            print(f"  Created: {user['username']}")

            response = await client.post(
                "/api/users/token",
                data={
                    "username": user_data["email"],
                    "password": user_data["password"],
                },
            )
            response.raise_for_status()
            token = response.json()["access_token"]

            if image_name := user_data.get("image"):
                image_path = POPULATE_IMAGES_DIR / image_name
                if image_path.exists():
                    response = await client.patch(
                        f"/api/users/{user['id']}/picture",
                        files={
                            "file": (
                                image_name,
                                image_path.read_bytes(),
                                "image/png",
                            ),
                        },
                        headers={"Authorization": f"Bearer {token}"},
                    )
                    response.raise_for_status()
                    print(f"    Uploaded: {image_name}")

            users.append(
                {"id": user["id"], "username": user["username"], "token": token},
            )

        print(f"\nCreating {len(POSTS) + 1} posts...")

        # First create POST_44 (will become oldest after date update)
        response = await client.post(
            "/api/posts",
            json={"title": POST_44["title"], "content": POST_44["content"]},
            headers={"Authorization": f"Bearer {users[0]['token']}"},
        )
        response.raise_for_status()
        print(f"  Created: '{POST_44['title']}'")

        # Create remaining posts in reverse (last in list = oldest, first = newest)
        for i, post_data in enumerate(reversed(POSTS)):
            user = users[i % len(users)]
            response = await client.post(
                "/api/posts",
                json={
                    "title": post_data["title"],
                    "content": post_data["content"],
                },
                headers={"Authorization": f"Bearer {user['token']}"},
            )
            response.raise_for_status()
            title = post_data["title"]
            print(
                f"  Created: '{title[:50]}...'"
                if len(title) > 50
                else f"  Created: '{title}'",
            )

        print("\nUpdating post dates...")
        await update_post_dates()

    await engine.dispose()

    print("\nDone!")
    print(f"  {len(USERS)} users")
    print(f"  {len(POSTS) + 1} posts")
    print("  Profile pictures saved locally")


if __name__ == "__main__":
    asyncio.run(populate())
