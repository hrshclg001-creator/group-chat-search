"""Hand-authored fictional decisions. Speaker numbers refer to P01 through P08.

Each episode has 12 messages. Interruptions stay in the chronological episode;
they are not labelled as retrieval targets. Conclusions are corpus audit data,
not evaluation ground truth.
"""

# (date, start time, speaker|text lines). One message every 2-5 minutes.
THREADS = {
    'TRIP_MANALI': [
        ('2026-03-08', '20:10', '''3|June break mein trip? Goa bol raha hu main since first year 😭
1|beach sounds good but kitna kharcha aayega from Indore
4|pehle total batao. sirf train ticket ko budget mat bolna
7|Manali bhi option hai, mountains > sunburn
3|Goa mein hostel le lenge toh cheap hoga na
5|guys kisi ke paas type c charger hai abhi
6|mere desk pe hai Kabir, wapas dena kal
2|dates tentatively 10 to 15 June? result date se clash mat karna
8|I can do those dates if return is by Monday morning
4|No booking yet. Compare both with food and local transport included.
7|haan
3|ok spreadsheet banaunga, abhi poll ko final mat samajhna'''),
        ('2026-03-12', '19:20', '''3|Goa estimate: travel 4200, stay 2800, food 1800, local 1600 per head
4|10400 already, aur buffer? mera absolute limit 9000 hai
1|Goa waala reel bola 5k mein sab 😅
8|that reel starts from Mumbai, hum Indore mein hain
7|Manali quote via Delhi approx 8200 including bus and shared rooms
2|overnight buses do back to back honge? motion sickness hoti hai mujhe
6|[Image] mess ka aaj ka mysterious orange sabzi
5|yeh food hai ya compiler warning 😂
3|Goa train sleeper try karu toh 1200 bach sakta hai
4|try availability first. Imaginary cheap ticket doesn't count
7|Manali stay mein hot water included hai, heater extra
2|send cancellation terms bhi. abhi dono open hain'''),
        ('2026-03-17', '21:05', '''7|[PDF] Manali guesthouse quote, 3 rooms for our eight
8|two triple rooms and one twin? who gets which baad mein
3|Goa sleeper seats waitlisted in the mock itinerary I made
1|flight toh budget se bahar. Overnight train plus bus manageable?
2|one rest stop in Delhi chahiye; continuous travel nahi
4|Revised hill plan 8700 with rest room and buffer. coast 10900
5|wait project ka submission kal 11 hai ya 5
6|5 pm. trip chat ke beech panic mat failao 😭
3|I still prefer sea, but 10900 is a lot
8|June mein rain contingency bhi sochna padega for either place
7|If roads look unsafe we cancel, no heroic driving plan
4|Agreed. Refundable room hold only, nobody pay yet'''),
        ('2026-03-23', '18:30', '''2|parents asked itinerary. Manali ya Goa? cannot send two PDFs forever
3|Last Goa pitch: reduce to 3 nights and skip scooter rental
4|Still 9900 in your sheet, plus two people can't ride
8|shared cabs eat the saving. I'd rather not split the group daily
1|Could postpone to December instead?
7|then internships and everyone's separate dates. June overlap is rare
5|meri cycle ki chain phir utar gayi, wonderful timing
6|walk back, I'll keep dinner. My vote is hills within 9k
2|With Delhi rest stop I'm okay with that route
3|fine yaar sea next time. don't book without cancellation clause
4|Goa rejected for this break because total exceeds our cap
8|We have agreement on constraints; final dates and deposit still pending'''),
        ('2026-03-28', '20:40', '''7|guesthouse can hold June 11-14 until tomorrow evening
2|Return June 15 morning works for me, checked family calendar
4|8700 ceiling includes a 700 emergency buffer, not shopping
5|do we need jackets in june or hoodie enough
8|layers le jana. Weather packing list baad mein bhejungi
3|[Image] my beach wallpaper has officially been betrayed
1|😂
6|Refundable until June 3, correct? quote ka last page tiny tha
7|yes, bus charges separate terms; note added in itinerary
4|Final decision: Manali, June 10-15, maximum Rs 8,700 each. Goa is dropped. Refundable rooms only; Aarav will collect Rs 2,000 each by April 2.
1|I'll track the eight contributions in one sheet. No payments posted here.
3|done, mountains it is 🏔️'''),
        ('2026-04-02', '19:10', '''1|Trip update: all eight deposits marked received in our plan
4|Please don't change the room allocation without checking with Meera
8|Ananya Sneha and me in room A, sorting the other five now
5|who took my blue notebook from lab
2|with me, thought it was mine. sorryyy
7|Delhi rest stop remains in the itinerary, not removing it to save 300
3|I saw another Goa deal but ignoring it. We already chose the hills
6|good. lets stop reopening the poll every time an ad appears
8|[PDF] June hill-trip itinerary revision 3, with refund notes
2|downloaded
4|Budget unchanged. Any optional activity comes out of personal spending
1|done. Next trip discussion only for packing or safety updates'''),
    ],
    'HACKATHON_STACK': [
        ('2026-04-10', '20:00', '''5|college hackathon idea: campus lost-and-found board? photo and location
1|MERN karte? Mongo, Express, React, Node. I have an old starter
6|Django and Postgres would give us admin quickly
4|Flutter app could look nice, camera upload simple
3|Can I pitch blockchain for proof of ownership lol
8|Please no tokens to retrieve my umbrella
2|We get 36 hours, demo must run on the lab laptop without internet
7|btw badminton court is locked again
5|guard ke paas key hai, ask before 8
6|What data actually needs storing? start there
1|items, claim requests, one staff approval flow
4|Okay options on table, no stack fixed tonight'''),
        ('2026-04-14', '18:20', '''6|I prototyped the claim table. We need relationships, not giant nested docs
1|Mongo can handle it but might be overkill for 200 fake items
5|Firebase? login and images done fast
2|Campus wifi died during last demo. Hosted dependency worries me
4|Flutter would mean emulator setup on judging laptop
3|[Voice message] rambling idea about a QR sticker on every lost item
8|QR as optional later. Core claim flow first please
7|Anyone coming for dosa? I ordered too much
6|save one. Local file db could solve the demo setup problem
1|Express still okay? I know the routing bits
2|Compare with a Python API; Sneha and Kabir can maintain that
5|I'll test uploads on both before we choose'''),
        ('2026-04-19', '21:10', '''5|upload test: my Node sample works but auth middleware is half copied
6|I tried a small Python service with typed request validation. Fewer moving parts
1|Django then?
6|not necessarily. Its admin is nice but most of our screens are custom
4|Design update: responsive website is sufficient; mobile app dropped
8|Can we keep the labels bilingual? claim button confused two friends
3|guys movie night cancel? everyone in stack debate 😂
7|postpone to Friday, projector remote missing anyway
2|SQLite supports the tiny offline demo. Why a separate database server?
1|For this scope I don't have a reason. MERN was just familiarity
5|We should write down the rejected options so we don't circle back
6|Yes, but pick after testing a clean laptop launch'''),
        ('2026-04-24', '19:30', '''1|clean launch test took 7 min with local db, longer with hosted services
5|Firebase rejected for demo because offline requirement is real
4|Flutter rejected too, responsive web is enough for judges
6|The big Python framework adds admin config we won't use. I'd drop it
2|Any reason to keep Mongo now? claim approval is transactional
1|No. Let's use SQL tables and include a small seed fixture
8|[Image] three possible claim-form layouts, vote for readability pls
3|middle one, first looks like railway form
7|printer in library jammed, unrelated but avoid sending jobs
4|Middle layout wins, keep text large
5|Need package names and responsibilities nailed down tomorrow
6|I'll send one final implementation note after endpoint tests'''),
        ('2026-04-27', '20:15', '''6|All local endpoint tests green on the borrowed laptop
2|Is there anything that still calls cloud services?
5|No. Demo images stay on disk, sample accounts are entirely fake
1|Frontend prototype is working, no state library needed
3|call it LostLoop? sounds like my coding life
8|LostLoop works, please don't spend two hours on logo
7|haan
4|Plain CSS is enough; I can finish the form tonight
6|Locked for LostLoop: React with Vite in JavaScript, FastAPI on Python, and SQLite for storage. Plain CSS, local image files, no cloud dependency. Aarav handles UI; Kabir and I handle API and schema.
1|Confirmed. Retiring the Express starter rather than mixing two servers
5|I'll write startup instructions so the judge can run it offline
2|Stack decision closed. Tomorrow we test the full claim journey'''),
        ('2026-05-03', '18:40', '''5|LostLoop now launches from the README on a fresh folder
1|Someone asked why no Mongo. We already settled on a local SQL file
6|Please don't add a second database over the weekend
4|[Image] final claim status card: pending, approved, declined
8|approved colour needs text also, don't rely only on green
3|my laptop fan is participating in the hackathon too ✈️
7|clean the vents after submission, not in middle of demo
2|Who's presenting rejection case? judges will ask
5|me. Fake duplicate claim should be declined with a reason
6|Good, keep sample identities fictional
1|done
8|Closing this planning thread. Bug reports can be regular chat now'''),
    ],
    'BIRTHDAY_EVENT': [
        ('2026-07-06', '20:10', '''8|My birthday is July 25. Small get-together? no surprise please 😂
3|rooftop dinner at Sky Lantern would be nice
4|What is our TOTAL cap, before people send aesthetic reels
8|3000 total including cake. Eight of us, nothing fancy
7|college lawn picnic? practically free venue
2|monsoon mein lawn gamble hai. Need indoor backup
5|bowling plus burgers sounds fun
1|that alone might be 500 each, already 4000
6|Unrelated: who has the extension board from yesterday
7|I do, bringing it after dinner
4|Let's compare rooftop, bowling, hostel common room, and cafe
8|yes. I'm part of planning, don't hide the spreadsheet from me'''),
        ('2026-07-10', '19:15', '''3|Sky Lantern quote is 650 per person, before birthday cake
4|5200 before cake. Rooftop rejected, way above 3000
5|Bowling student slot 320 each, food separate
2|2560 leaves 440 for cake AND food for eight. impossible
8|Skip bowling too, I want time to talk anyway
7|Common room is free if warden approves visitors
1|Can day scholars enter after 7? rule was changed last semester
6|I'll ask, don't assume. Also canteen closes early on Saturdays
3|[Image] orange cat occupying my entire chair
8|invite cat, budget unchanged
4|😂
2|Cafe option still open. Get an actual quote, not menu screenshots'''),
        ('2026-07-14', '21:00', '''6|Hostel common room can't allow outside students after 6 that day
1|I have family work till 6. Won't reach by then
7|Lawn plus borrowed canopy?
2|Rain and permission both uncertain. Dropping lawn
4|Then common room also out unless we split group, which we won't
8|Please don't split. We only get all eight together sometimes
3|Nukkad Cafe side room asks minimum 2400 spend, no room fee
5|Cake allowed from outside?
3|Yes if we clean up; no decoration on walls
6|wifi went again, sending from mobile data. sorry if duplicate
4|Need tax included in 2400 and exact snack portions confirmed
8|Sounds promising but hold off until the final quote'''),
        ('2026-07-18', '18:45', '''3|Cafe says 2400 includes tax: eight snack plates and eight drinks
4|Cake quote is 500 for half kilo, simple chocolate
2|2900 total leaves 100. Candles? plates?
8|I have reusable plates and candles from home
5|Half kg enough? eight small slices yes, after snacks
7|Could get larger cake for 800 and skip drinks
4|That breaks the cafe minimum package. Better keep current plan
1|anyone seen my umbrella near lab? grey, broken handle
6|security desk, I left it there
2|Time window? I have a call until 6:30
3|Side room available July 25, 7 to 9 pm
8|Works for me. Let's confirm after everyone responds'''),
        ('2026-07-21', '20:30', '''1|July 25 after 7 confirmed from my side
6|same, back from home by afternoon
5|me too. vegetarian snacks only right?
3|yes all eight plates veg, confirmed in quote
7|no rooftop rain roulette, good choice
2|Can someone post one final message? too many prices above
4|Final birthday plan: July 25, 7-9 pm, Nukkad Cafe side room for all eight. Rs 2,400 snacks/drinks + Rs 500 chocolate cake = Rs 2,900 total, capped at Rs 3,000. Split Rs 362.50 each. No decorations purchase. Rohan reserves the room; Sneha collects the cake.
8|Perfect. I'm paying my share too, no arguments ❤️
6|Cake pickup at 6:15 noted. I will bring the candles from Meera
5|[Image] tragic attempt at a homemade birthday card
1|actually cute yaar
3|Room reserved. No more venue polls'''),
        ('2026-07-25', '22:10', '''8|Home! thank you all, exactly the quiet birthday I wanted 🥹
2|Reached hostel, sending photos after charging
6|Cake was 500 as quoted, no extra box charge
3|Cafe bill 2400, same as reservation. Kept the receipt
4|Actual total 2900, equal shares 362.50. No buffer spent
7|and not a single wet lawn chair, amazing
5|[Image] eight plates and one badly cut cake
1|we did geometry all semester for THIS cutting 😭
8|The card is staying on my desk. Even Kabir's spelling
5|birhtday is a design choice
6|😂
4|Budget closed, receipt in shared folder. Thanks for keeping it simple'''),
    ],
}

# Exact conclusion positions (zero-based within episode) for corpus auditing.
CONCLUSIONS = {'TRIP_MANALI': (4, 9), 'HACKATHON_STACK': (4, 8), 'BIRTHDAY_EVENT': (4, 6)}
