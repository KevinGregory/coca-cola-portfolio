# campaigns.py
# This file contains the data for each Coca-Cola campaign we're analyzing.
# Each campaign is a dictionary with all the info BAML needs to analyze it.
# You can add more campaigns by following the same structure.

CAMPAIGNS = [
    {
        # Campaign 1: The most iconic Coke ad ever made
        "id": "buy_the_world",
        "name": "I'd Like to Buy the World a Coke",
        "agency": "McCann Erickson",
        "year": 1971,
        "brief": (
            "Create a global ad that positions Coca-Cola as a symbol of peace, "
            "unity, and shared humanity during a turbulent era of the Vietnam War "
            "and civil rights movements."
        ),
        "ad_description": (
            "A hilltop in Italy. Hundreds of young people from different countries "
            "stand together holding Coca-Cola bottles, singing 'I'd like to buy the "
            "world a home and furnish it with love...' The camera pulls back to reveal "
            "a massive mosaic of humanity. The tagline: 'It's the real thing.' "
            "Originally a radio jingle called 'True Love and Apple Trees', reworked "
            "into a full TV commercial. Later became a standalone pop hit."
        ),
        "color": "#E63946",  # For HTML portfolio display
    },
    {
        # Campaign 2: Personalization at massive scale
        "id": "share_a_coke",
        "name": "Share a Coke",
        "agency": "Ogilvy Australia",
        "year": 2011,
        "brief": (
            "Reverse declining sales among Australian teens and young adults by "
            "making Coca-Cola feel personal and shareable. Replace the Coke logo "
            "on bottles with 150 of Australia's most popular names."
        ),
        "ad_description": (
            "Coke bottles and cans replace the iconic logo with popular first names "
            "like 'Share a Coke with Sarah'. TV spots show friends finding their names "
            "and sharing bottles. OOH displays let people search for their name. "
            "A social campaign invites people to post photos with their named bottle. "
            "Personalized bottles available at kiosks in malls. Tagline: 'Share a Coke'."
        ),
        "color": "#E63946",
    },
    {
        # Campaign 3: Christmas and Coke are now inseparable
        "id": "holidays_coming",
        "name": "Holidays Are Coming",
        "agency": "McCann Erickson",
        "year": 1995,
        "brief": (
            "Own the Christmas season for Coca-Cola by creating an emotionally resonant, "
            "cinematic holiday ad that becomes a perennial tradition. Use the Coca-Cola "
            "trucks to create a magical, anticipated annual event."
        ),
        "ad_description": (
            "A dark winter night in a small town. A convoy of illuminated Coca-Cola "
            "trucks — red with white lights — rolls through snowy streets. Children "
            "run to the windows, mouths agape. The jingle 'Holidays are coming, holidays "
            "are coming' plays. Santa appears on a billboard, winks. The trucks bring "
            "light and joy. Ends on the Coca-Cola logo. Pure seasonal magic with zero "
            "product messaging — just feeling."
        ),
        "color": "#E63946",
    },
    {
        # Campaign 4: Post-recession optimism reframe
        "id": "open_happiness",
        "name": "Open Happiness",
        "agency": "Wieden+Kennedy",
        "year": 2009,
        "brief": (
            "Launch a global platform that repositions Coca-Cola as a source of "
            "optimism and small everyday joys during the 2008 financial crisis. "
            "Counter the doom of the recession with accessible, real happiness."
        ),
        "ad_description": (
            "Multiple executions across TV, print, and digital. Key TV spot: "
            "A Coke vending machine in a college campus starts giving out free Cokes "
            "and food to students who interact with it. Strangers bond over unexpected "
            "gifts. Upbeat music. Smiles everywhere. Print: Simple photography of "
            "people in genuine moments of joy holding a Coke. Tagline: 'Open Happiness'. "
            "Ran in 200+ countries simultaneously."
        ),
        "color": "#E63946",
    },
    {
        # Campaign 5: The most recent platform shift
        "id": "real_magic",
        "name": "Real Magic",
        "agency": "WPP / OpenX",
        "year": 2021,
        "brief": (
            "Replace 'Open Happiness' with a new global platform that speaks to "
            "Gen Z's desire for authentic human connection in a fragmented, digital-first "
            "world. Acknowledge complexity and imperfection — not forced positivity."
        ),
        "ad_description": (
            "Hero film 'One Coke Away From Each Other': gamers in a tournament — "
            "an esports arena filled with players from different backgrounds — reach "
            "a moment of genuine connection over a shared Coke. The visual language "
            "blends real footage with gaming aesthetics. Authentic, unpolished moments. "
            "The 'Hug' logo — a new Coca-Cola wordmark enclosed in a hug shape — debuts. "
            "Ran across TV, digital, social, and in-game placements."
        ),
        "color": "#E63946",
    },
]
