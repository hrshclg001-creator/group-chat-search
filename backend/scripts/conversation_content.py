"""Eight-message conversation vignettes with shared episode-level details.

Roles 0-3 are assigned to four different participants per episode. Recurring
college routines intentionally repeat; dates, topics and wording slots vary.
Months restrict academic and vacation scenes to a fictional college calendar.
"""

ALL = (3, 4, 5, 6, 7, 8)
TERM = (3, 4, 8)
SCENES = [
    ('food', ALL, '''0|{opening} {food} khane chale? mess menu dekh ke himmat nhi hui
1|kitne baje
0|{meet_time}, usual gate pe
2|I have only {cash} left for today 😭
3|share kar lenge, just don't order three drinks again
1|haan
2|fine. {food} ke liye aa raha hu
3|I'll bring change. UPI pe network gaya toh phir drama'''),
    ('food', ALL, '''0|[Image] {food} looked better on the menu ngl
1|why is it so flat 😭
2|taste kaisa hai
0|okay-ish, too much {ingredient}
3|ask them to replace it if it's cold
0|nah warm hai. presentation bas tragic
1|MasterChef hostel edition
2|😂'''),
    ('food', ALL, '''0|Forwarded: Student meal combo at {shop}, today only. Ask at counter for details.
1|is this another old forward
2|date toh aaj ka lag raha, {date_label}
3|still call before going. last time shop hi band thi
0|haan checking, kisi ko abhi mat leke nikalna
2|I can walk past at {meet_time}
1|thanks
3|buy only if normal price se actually cheaper ho'''),
    ('food', ALL, '''0|tried making {food} in the shared kitchen
1|kettle mein??
0|nooo proper pan. learnt after last disaster
2|{ingredient} add kiya?
0|too much accidentally, ab balance kaise karu
3|make a smaller plain batch and mix it
1|[Voice message] laughing while offering completely useless cooking advice
2|ignore that audio, actual advice upar hai'''),
    ('coding', ALL, '''0|{bug} aa raha in my {language} practice code
1|paste minimal example, entire repo mat bhejna
0|https://example.com/snippets/{episode_slug}
2|Line with {code_detail} check karo, input shape wrong lag raha
3|I can reproduce with empty input too
0|ohhh yes. copied assumption from yesterday's exercise
1|add that case before fixing, warna wapas aayega
0|done, thanks. almost laptop ko blame kar diya'''),
    ('coding', ALL, '''0|anyone doing {exercise} tonight? stuck on second example
1|I got brute force, complexity bahut bad hai
2|start with tiny input and draw it
0|[Image] notebook trace with arrows all over the page
3|third arrow backwards hai. state changes after this step
1|oh same mistake meri bhi
0|samajh gaya, let me rewrite without watching solution
2|nice, explain it tomorrow if it still makes sense'''),
    ('coding', ALL, '''0|git mein {git_problem}. Did I lose the whole assignment?
1|stop clicking random buttons first 😅
2|save a copy of your current files, then inspect status
0|okay backup ban gaya
3|send just the error text, no tokens or private files
0|It's only my toy repo. https://example.com/practice/{episode_slug}
1|we can look after {meet_time}
0|thanks, panic thoda kam hua'''),
    ('coding', ALL, '''0|https://docs.python.org/3/tutorial/ useful section for {exercise}
1|bookmarked
2|I keep reading docs then forgetting to actually code
3|same. one small example khud type karo
0|I changed the sample input and immediately broke mine lol
1|that's how you find what you didn't understand
2|deep baat before chai
3|😂'''),
    ('movies', ALL, '''0|{movie} dekhne ka mood hai tonight
1|rewatch? you already know every line
0|comfort movie hai yaar
2|No spoilers pls, I haven't watched it
3|I can join after {meet_time}, headphones launga
1|pause if I get disconnected, don't finish without me again
2|haan
0|okay, link nahi bhej raha until everyone is free'''),
    ('movies', ALL, '''0|finished {movie}. that ending??
1|SPOILER mat likhna please
0|okay okay, vague reaction only 😭
2|music acha tha?
0|yes, especially the quiet scene near the end
3|I fell asleep halfway, meri review invalid
1|you fall asleep in trailers also
3|sleep is my strongest subject'''),
    ('movies', ALL, '''0|[Image] hand-drawn poster inspired by {movie}
1|this is actually nice, text thoda chota hai
2|colour combo reminds me of our lab notice board
0|not the compliment I expected 😂
3|increase contrast, phone pe title disappear ho raha
0|okay exporting another version
1|send later, no rush
2|and watermark your original drawing before public posting'''),
    ('random', ALL, '''0|whose {lost_item} is lying near {place}
1|colour?
0|{colour}, has a small scratch on one side
2|mine maybe, I'll describe the sticker privately
3|don't leave it unattended there
0|handing it to the desk staff, ask them at {meet_time}
2|thanks!
1|group chat doing actual public service for once'''),
    ('random', ALL, '''0|wifi down for anyone else or only my cursed laptop
1|phone pe bhi nahi chal raha
2|router light red near {place}
3|maintenance notice tha na
0|where?? 200 unread msgs mein buried hoga
2|Forwarded: Campus network maintenance, {date_label}, service may be interrupted. Save work locally.
1|classic, notice works only if internet works
3|😂'''),
    ('random', ALL, '''0|[Image] cat sleeping on my {lost_item}
1|new owner mil gaya
2|do not disturb the administrator
0|I need it in ten minutes 😭
3|offer an empty cardboard box nearby
1|cat chooses box, human gets freedom
0|worked actually
2|strong debugging skills'''),
    ('random', ALL, '''0|phone battery {battery}% and charger at home. incredible planning
1|meet me near {place}, powerbank hai
2|bring cable yourself, theirs is ancient
0|type c hai mere paas
3|remember to give it back this time
0|one time hua tha yaar
1|three
2|😂'''),
    ('random', ALL, '''0|good morning
1|it's {meet_time}
0|emotionally morning
2|respect
3|did anyone actually sleep on time yesterday
1|I tried, then doomscrolled for an hour
0|same :/
2|aaj phone desk pe rakh ke sona, pillow ke neeche nahi'''),
    ('random', ALL, '''0|[Voice message] telling a long story about getting on the wrong bus near {place}
1|can't listen rn, two line summary?
0|wrong direction. got off next stop. walking back 😭
2|safe ho na? busy road pe phone mat use karo
0|yes waiting at tea stall now
3|share nearest landmark when stationary
1|I can call after {meet_time}
0|all good, correct bus aa gayi'''),
    ('travel', ALL, '''0|anyone taking the {route} bus around {meet_time}
1|maybe, depends how long my errand takes
2|queue long hai today, keep some extra time
3|don't reserve a seat with my bag, last time argument ho gaya
0|haan we'll queue normally
1|Reached stop. Where are you?
0|other side 😭 crossing at signal
2|take your time, another bus will come'''),
    ('travel', ALL, '''0|[Image] sunset from the road near {place}
1|Indore giving free wallpapers again
2|which camera filter
0|none, dirty bus window did the editing
3|😂
1|save original quality also
2|caption: public transport cinematic universe
0|using that, credit chai mein milega'''),
    ('events', ALL, '''0|community {activity} session this evening at {place}, anyone free?
1|beginner allowed? I'm genuinely terrible
2|that's half of us, aa jao
3|need to bring anything?
0|water and comfortable shoes, no fees for our little group
1|{meet_time} tak aaunga
2|okay, don't block the entrance while waiting
3|done'''),
    ('college', TERM, '''0|{subject} assignment ka {task} samajh aaya kisi ko?
1|I read it twice and understood less the second time
2|{faculty} said focus on explanation, not just final answer
0|[PDF] {subject} practice sheet for {date_label}, class copy
3|page 2 ka diagram missing from my download
1|same, maybe export problem
2|I'll ask during consultation tomorrow, don't invent the missing values
0|thanks. tab tak first two questions karte'''),
    ('assignments', TERM, '''0|submission portal {task} upload nahi le raha
1|file size kitna hai
0|{file_size} MB, screenshots bahut ho gaye
2|compress images, keep text readable
3|and check PDF opens after export. mine was blank once
0|now accepted. finallyyyyy
1|save acknowledgement locally
0|done, coffee earned'''),
    ('college', TERM, '''0|Forwarded: {subject} tutorial shifted to room {room} on {date_label}. Please check the class noticeboard.
1|old room pe khada hu main 😭
2|come one floor up, still five minutes left
3|is it tutorial or lab?
0|tutorial. lab timing unchanged in this notice
1|okay running
2|walking is fine, staircase slippery hai
3|haan, attendance se pehle bones important'''),
    ('assignments', TERM, '''0|Anyone proofreading {subject} writeup at {meet_time}?
1|I can check diagrams, no promises on theory
2|Please flag mistakes, don't copy each other's paragraphs
0|yes own solutions. mine has spelling errors everywhere
3|send your rough explanation first
0|[Image] rough explanation of {task}, arrows very messy
1|second label cut off, export margin badhao
0|good catch, thnks'''),
    ('college', TERM, '''0|printer near {place} ate my last page
1|did it at least print the first ones correctly
0|yes but page numbers missing, of course
2|library printer might work, check queue first
3|PDF version phone pe rakhna in case
0|https://example.com/class-notes/{episode_slug}
1|nice filename: final_final_really_final 😂
2|don't rename it again until it actually prints'''),
    ('college', TERM, '''0|{subject} lab mein partner swap allowed hai kya today
1|ask {faculty}, don't assume based on last week
2|why swap?
0|my partner arriving late because bus broke down
3|start reading the procedure meanwhile
1|I can help explain {task}, can't sign for anyone
0|fair, will ask directly
2|good. lab coat bhi yaad rakhna this time'''),
    ('assignments', TERM, '''0|{subject} group presentation slides kitni honi chahiye
1|time limit matters more, we get five minutes
2|ours has 18 slides, disaster incoming
3|cut duplicated background, keep one example for {task}
0|agree. who handles intro?
1|I can, but someone time me at {meet_time}
2|done
3|[Voice message] trying a 20-second intro and stumbling over the title'''),
    ('college', TERM, '''0|library mein {subject} reference book mil gayi finally
1|can you keep it forever for our batch 😂
0|nope due {due_date}, others need it too
2|write edition number, examples changed in newer one
3|I only need help finding chapter for {task}
0|index mein check karunga, no scanning whole book
1|thanks
2|return reminder laga dena, fine quietly grows'''),
    ('exams', (4, 5), '''0|{subject} revision start ki ya everyone pretending
1|opened syllabus, closed it, progress
2|{task} is my weak area
3|let's solve two examples at {meet_time}, no marathon plan
0|I'll bring rough sheets
1|[PDF] self-made {subject} revision checklist, no official predictions
2|good, those guaranteed question forwards are nonsense
3|haan concepts pe focus'''),
    ('exams', (4, 5), '''0|Forwarded: Someone claims these are sure-shot exam topics for {subject}. Unverified forward, not an official paper.
1|Please don't rely on this
2|half of it isn't even our syllabus
3|use {faculty}'s class outline instead
0|agreed, sharing only to warn, not as actual answers
1|thanks for clarifying
2|I still need help with {task}, legitimate notes anyone?
3|I'll explain after {meet_time}'''),
    ('exams', (4, 5), '''0|mock test mein {subject} ke steps miss kar diye
1|marks se pehle identify which step went wrong
2|time ran out or concept?
0|both 😭 spent ten minutes on {task}
3|do a smaller timed set tomorrow, review immediately after
1|and sleep. all-night revision se worse hota mere saath
0|okay. today only corrections, no new chapter
2|sensible'''),
    ('exams', (4, 5), '''0|[Image] revision desk: four pens, zero motivation
1|I have motivation but no working pen, exchange?
2|exam hall checklist: ID, pens, water. no last minute drama
3|{subject} notes close kar raha at {meet_time}
0|I'll do one recap of {task} then same
1|all the best
2|you too
3|gn'''),
    ('exams', (5,), '''0|practice paper done, don't ask marks yet
1|fair. food first?
2|{food} sounds good
3|I got stuck at {task}, discuss after break?
0|yes but please no shouting answers across canteen
1|😂
2|meet {meet_time} near {place}
3|done, bringing my rough solution'''),
    ('travel', (6,), '''0|packing for home and somehow bag heavier than me
1|remove the three books you know you won't read
2|carry charger in small bag, not deep inside suitcase
0|good reminder. almost forgot {lost_item} also
3|travel day ke screenshots offline save kar lena
1|and check platform at station, forwards are unreliable
0|haan. will message when reached
2|safe journey'''),
    ('travel', (6,), '''0|reached home, finally actual {food}
1|parcel bhej do please
2|ghar jaake bhi group mute nahi kiya?
0|can't miss the daily nonsense
3|[Image] my equally chaotic unpacking situation
1|why is there a spoon in your laptop sleeve
3|backup engineering
2|😂'''),
    ('travel', (6,), '''0|local walk near home today, no big travel plan
1|photos?
0|[Image] quiet lane after evening rain
2|nice. slippery toh nahi?
0|main road dry hai, stayed off muddy path
3|I'm just walking to buy {food}, does that count
1|absolutely
2|fitness with incentives'''),
    ('random', (6,), '''0|home routine: breakfast, random chores, forgot what day it is
1|{date_label}. group calendar service available
2|I've become family tech support full time
3|same, fixed printer and then got asked to fix television
0|do they also say bas do minute ka kaam hai
1|every time 😭
2|I'll practice {exercise} after {meet_time}, join if free
3|maybe, next appliance may interrupt'''),
    ('travel', (6,), '''0|Found old hill-trip photos while clearing storage
1|don't delete originals before backing up
2|[Image] mountains mostly hidden behind a very enthusiastic thumb
3|professional composition
0|that thumb has seen things
1|😂
2|Next time rotate phone before starting video please
3|No new trip planning tonight, bank balance needs rest'''),
    ('coding', (6, 7), '''0|internship practice task: {task} in {language}, small demo only
1|real company data toh nahi use kar rahe?
0|nope synthetic examples, completely local
2|good. what is blocking you
0|{bug}, mostly when input empty
3|write the empty-input case first then normal case
1|share a minimal fictional snippet later
0|done, I'll clean it up after {meet_time}'''),
    ('college', (7,), '''0|anyone doing mock interview practice today
1|yes but easy warmup first, confidence fragile
2|explain {exercise} out loud, no code for first five minutes
3|I'll be interviewer, polite version
0|{meet_time} works?
1|haan
2|I'll keep feedback about explanation separate from correctness
3|nice. don't make us memorise company trivia'''),
    ('coding', (7,), '''0|[PDF] my internship weekly learning log, personal details removed
1|first paragraph is too vague
2|add what you tried and what failed
0|mention {bug} and how I investigated?
3|yes, much better than saying learned many things
1|keep it short, mentor has other work too
0|ok
2|and fix spelling of recieved before sending 😅'''),
    ('events', (7, 8), '''0|club wants volunteers for {activity} session
1|what work exactly? registration or setup
2|setup at {place}, registration team already full
3|I can spare one hour around {meet_time}
0|fine, no need to miss class for it
1|[Image] draft directional sign, arrow may be backwards
2|it is backwards 😭 rotate arrow, not whole poster
3|saved several lost freshers today'''),
    ('college', (8,), '''0|new semester timetable mein {subject} room {room} hai?
1|provisional version says that, check after lunch too
2|Forwarded: Timetable is provisional; confirm changes on the department board before attending.
3|I printed it already, naturally
0|pencil se mark kar lo changes
1|at least we won't trust last semester's screenshot
2|someone definitely will
3|probably me'''),
    ('college', (8,), '''0|freshers asked where {place} is, I gave directions badly
1|landmarks use karo, east west mat bolo
2|draw a tiny map from main gate
0|[Image] very questionable hand-drawn campus map
3|you put library on wrong side 😭
1|I'll walk them there, easier
2|thanks, map ko art exhibition bhej do
0|deserved'''),
    ('assignments', (8,), '''0|first {subject} assignment and already confused about {task}
1|new notebook optimism lasted two days
2|read the example from tutorial first
3|we can discuss approach at {meet_time}, then write individually
0|works. submission {due_date} in my calendar
1|verify date with actual notice too
2|yes our schedule changes a lot
3|done'''),
    ('events', (3, 4, 8), '''0|{activity} rehearsal today, {place} available?
1|there was another group there earlier
2|ask the coordinator before moving their equipment
3|I'll check at {meet_time}
0|thanks, meanwhile practise without speakers
1|[Voice message] counting beats and losing track halfway
2|😂
3|that's why we need rehearsal'''),
    ('random', ALL, '''0|small win: cleaned desk and found my {lost_item}
1|under the same pile you said you checked yesterday?
0|maybe
2|congratulations to the search committee
3|I should clean mine, found a receipt from March
1|keep receipts till expenses settled, then sort
0|keeping one box for important papers now
2|we'll ask for proof next week'''),
    ('food', ALL, '''0|tea break near {place} at {meet_time}?
1|I'll take coffee actually
2|same stall? chai uncle knows our order better than us
3|don't order mine yet, running late
0|okay, waiting before buying anything
1|{food} available there today?
2|will check, not promising
3|thanks, five mins'''),
    ('random', ALL, '''0|song stuck in my head, can't remember name
1|lyrics ya tune?
0|[Voice message] humming three unrecognisable notes
2|bro that's the microwave beep
3|😂
0|noooo actual song, heard near {place}
1|send clearer version later, abhi impossible
2|meanwhile microwave remix goes hard'''),
    ('coding', ALL, '''0|made a tiny {language} tool for tracking my own reading
1|nice, screenshot?
0|[Image] plain page with three books and a very crooked button
2|crooked button has personality
3|does it keep entries after restart?
0|not yet, that's tomorrow's task
1|good next step. no need to add 20 features
2|ship the save button first 😅'''),
    ('random', ALL, '''0|rain started here, anyone left clothes outside
1|YES my towel 😭
2|I'm near the rack, which one
1|{colour}, plain, next to window
3|bring your own stuff inside too
2|done, both on indoor stand
0|hero
1|owe you {food}'''),
    ('college', TERM, '''0|{faculty} explained {task} differently today
1|different method or different result?
0|method. My old notes skip two intermediate steps
2|write both side by side, see assumptions
3|[Image] rough comparison from {subject} notebook
1|third line makes sense now
0|yes, I was applying the shortcut outside its conditions
2|good catch, highlight that limitation'''),
    ('events', (3, 4, 7, 8), '''0|[PDF] draft {activity} session checklist, still needs review
1|extension board missing from list
2|and drinking water, every time we forget
3|is {place} accessible without stairs?
0|there's a ramp through side entrance, will confirm it's open
1|mention that on the invite once confirmed
2|I'll check supplies at {meet_time}
3|thanks'''),
    ('food', ALL, '''0|ordered {food}, got somebody else's parcel
1|don't open further, call counter
2|receipt number match?
0|nope, only noticed after reaching {place}
3|ask them to arrange swap safely, don't share someone's number here
0|they're checking. keeping package sealed
1|good
2|dinner has side quests again'''),
    ('random', ALL, '''0|any good book recs? something short between tasks
1|fiction or nonfiction
0|fiction, no productivity advice pls
2|check library short story shelf near {place}
3|I can lend one after {meet_time}, remind me
0|thanks, I'll return by {due_date}
1|look at us making realistic deadlines for once
2|😂'''),
    ('coding', ALL, '''0|pair programming anyone? {language} exercises for half an hour
1|I can watch and ask annoying questions
2|that's literally the job
3|start with {exercise}, I got stuck there
0|{meet_time}, no full solution paste until we try
1|okay. I keep getting {bug}
2|we'll compare inputs first
3|done'''),
]

SLOTS = {
    'opening': ['guys', 'oye', 'sunooo', 'helloo', 'anyone free?', 'arre'],
    'food': ['poha-jalebi', 'masala dosa', 'veg momos', 'samosa', 'pav bhaji', 'rajma rice', 'aloo paratha', 'idli', 'chole kulche', 'sandwich', 'sev puri', 'veg rolls'],
    'ingredient': ['salt', 'chilli', 'oil', 'garam masala', 'lemon'],
    'shop': ['Campus Corner', 'Chai Junction', 'Bun Basket', 'Morning Tiffin'],
    'subject': ['DBMS', 'Operating Systems', 'Computer Networks', 'Discrete Maths', 'Data Structures', 'Software Engineering'],
    'faculty': ['our tutor', 'the lab instructor', 'the course coordinator'],
    'language': ['Python', 'JavaScript', 'Java', 'C++'],
    'bug': ['an index error', 'a missing import error', 'a timeout', 'wrong output', 'a null value', 'an infinite loop'],
    'code_detail': ['the loop boundary', 'the return statement', 'the input parser', 'the counter reset'],
    'exercise': ['binary search', 'stack operations', 'graph traversal', 'sorting', 'hash maps', 'recursion', 'string parsing', 'queue operations'],
    'git_problem': ['merge conflict aa gaya', 'wrong branch pe commit hua', 'push rejected aa raha', 'changes unstaged dikh rahe'],
    'movie': ['3 Idiots', 'Swades', 'Queen', 'Dangal', 'Zindagi Na Milegi Dobara', 'The Lunchbox', 'Piku', 'Hera Pheri', 'Udaan', 'Chhichhore'],
    'lost_item': ['water bottle', 'notebook', 'pencil case', 'umbrella', 'headphones', 'calculator'],
    'place': ['the main gate', 'the library entrance', 'the stationery shop', 'the bus stop', 'the sports ground', 'the canteen'],
    'colour': ['blue', 'grey', 'green', 'black', 'yellow', 'purple'],
    'route': ['Vijay Nagar', 'Bhawarkuan', 'Rajwada', 'Palasia'],
    'activity': ['music', 'badminton', 'drama', 'photography', 'debate', 'volunteer orientation'],
}

TASKS = {
    'DBMS': ['normalisation example', 'SQL join exercise', 'transaction schedule', 'ER diagram'],
    'Operating Systems': ['page replacement trace', 'process scheduling table', 'deadlock example', 'memory allocation diagram'],
    'Computer Networks': ['subnetting example', 'routing table exercise', 'packet header diagram', 'TCP handshake explanation'],
    'Discrete Maths': ['induction proof', 'set relation exercise', 'counting example', 'truth table'],
    'Data Structures': ['tree traversal', 'linked list exercise', 'heap insertion trace', 'stack implementation'],
    'Software Engineering': ['use case diagram', 'test case table', 'requirements review', 'sequence diagram'],
}
