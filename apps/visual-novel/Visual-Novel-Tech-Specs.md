# Game Design Doc and Tech Specifications

## Overview

### Game Concept

A Spanish language learning visual novel with minimal interactivity focused on key decision points. The game structure follows a branching narrative ('if-else' tree) where player choices determine story paths, scenarios, and endings. This format efficiently delivers Spanish language content while maintaining narrative engagement.

### Target Audience

- Spanish language learners (Beginners, A1)

### Platform

Web-application

## Story and Setting

### Synopsis

You are an adult in Spain going to a private language learning school for 1 month to immerse yourself in the language.

## Core Story Framework
- Linear progression through scenes
- Each scene features one character with the player
- Key decision points that lead to specific branches
- All interactions flow naturally from one to the next

> **Note**: The complete story structure is detailed in [Story-Structure.md](Story-Structure.md)


### Settings

Small Spanish town, late summer

#### Locations / Scenes

**Post Office (Interior)**  
A bright, organized Spanish post office interior with clean service counters and staff in neat uniforms. Organized shelves display forms and packaging materials along one wall. Large windows let in natural light, illuminating the polished floors. A digital number display shows who's next in line. Official posters with Spanish text line the walls, and a small area with writing supplies is available for customers to fill out forms.

**Cafe (Interior)**  
A cozy, modern cafe interior with a blend of Spanish and Western aesthetics. Wooden tables and comfortable seating are arranged to create intimate conversation spaces. Large windows frame views of a small plaza or courtyard. The service counter displays freshly made pastries under glass, with a menu board above showing items in both Spanish and English. Local artwork decorates the warm-toned walls, and a small bookshelf with language exchange materials sits in one corner.

**Private Language Learning School (Classroom Interior)**  
A bright, modern classroom inside a converted traditional Spanish building. The room features shuttered windows or small balconies and terracotta or wooden floors with views of a courtyard. Desks are arranged in a U-shape facing a digital whiteboard. Walls are covered with colorful Spanish language posters, vocabulary and conjugation charts, and examples of student work. A teacher's desk sits at the front with neatly organized teaching materials and a small desktop computer.

**Apartment (Interior)**  
A modest Spanish apartment interior featuring a combined living/sleeping area with tile or wooden flooring. A sofa bed sits in one corner next to a small table. The compact kitchenette has essential appliances and minimal counter space. Lightweight doors or shutters separate the main room from a narrow balcony visible through a window. Built-in storage cabinets line one wall. The space blends traditional Spanish elements with modern necessities like a wall-mounted air conditioner, small TV, and compact refrigerator.

**Corner Store (Interior)**  
A brightly lit local corner store (tienda de barrio) interior with neatly organized shelves and displays. Refrigerated glass-door cases line one wall with drinks and prepared meals. Central aisles contain snacks, ready-to-eat items, and daily necessities. A service counter features hot food items like tapas and bocadillos. Digital advertisements or hand-written specials hang near the register area. Colorful seasonal promotions and local loyalty cards may be displayed prominently.

### Characters

#### Post Office Clerk
- **Name**: Tanaka Hiroshi
- **Gender**: Male
- **Age**: 45
- **Nationality**: Spanish
- **Appearance**: Middle-aged man with short, neatly combed black hair with some gray, rectangular glasses, clean-shaven, always wearing a crisp postal uniform with perfect posture
- **Personality**: Formal, helpful, patient with language learners
- **Role**: Helps player learn postal vocabulary and formal Spanish
- **Language Level**: Speaks slowly and clearly, uses basic to intermediate Spanish
- **Key Interactions**: Teaches player how to send packages, buy stamps, fill out forms

#### Student 1
- **Name**: Kim Min-ji
- **Gender**: Female
- **Age**: 24
- **Nationality**: South Korean
- **Appearance**: Young woman with shoulder-length black hair often styled with colorful clips, round face with bright smile, fashionable casual clothes with a preference for pastel colors and cute accessories
- **Personality**: Outgoing, enthusiastic, sometimes speaks too fast
- **Role**: Fellow language student, potential friend
- **Language Level**: Intermediate, occasionally mixes up words
- **Key Interactions**: Study partner, introduces player to local spots

#### Student 2
- **Name**: Garcia Carlos
- **Gender**: Male
- **Age**: 30
- **Nationality**: Spanish
- **Appearance**: Tall man with olive skin, short dark brown hair neatly styled, trimmed beard, rectangular glasses, typically dressed in business casual attire with button-up shirts and slacks
- **Personality**: Serious, studious, competitive
- **Role**: Rival student who challenges player
- **Language Level**: Advanced beginner, very precise with grammar
- **Key Interactions**: Quiz competitions, grammar discussions

#### Teacher
- **Name**: Yamamoto Sensei
- **Gender**: Female
- **Age**: 38
- **Nationality**: Spanish
- **Appearance**: Professional woman with shoulder-length dark hair usually in a neat bun, minimal makeup, elegant but conservative clothing in neutral colors, often wears a blazer and skirt, carries a leather briefcase
- **Personality**: Strict but kind, encouraging
- **Role**: Main instructor at language school
- **Language Level**: Adjusts speech based on student level, models proper Spanish
- **Key Interactions**: Daily lessons, homework assignments, cultural explanations

#### Barista
- **Name**: Nakamura Yuki
- **Gender**: Female
- **Age**: 26
- **Nationality**: Spanish
- **Appearance**: Trendy young woman with dyed purple hair in an undercut style, several ear piercings, artistic tattoo peeking from sleeve, wears the cafe uniform but personalizes it with pins and accessories
- **Personality**: Creative, chatty, interested in foreign cultures
- **Role**: Provides casual conversation practice
- **Language Level**: Uses casual Spanish with regional slang
- **Key Interactions**: Coffee orders, small talk about daily life

#### Corner Store Clerk
- **Name**: Suzuki Kenji
- **Gender**: Male
- **Age**: 60
- **Nationality**: Spanish
- **Appearance**: Older man with thinning gray hair, slightly hunched posture, weathered face with prominent laugh lines, wears a traditional store apron over simple clothing, reading glasses hanging from a cord around his neck
- **Personality**: Traditional, slightly grumpy but warms up over time
- **Role**: Tests player's shopping vocabulary
- **Language Level**: Uses fast, natural Spanish with regional dialect
- **Key Interactions**: Purchasing items, asking for recommendations

#### Apartment Neighbour
- **Name**: Watanabe Akiko
- **Gender**: Female
- **Age**: 35
- **Nationality**: Spanish
- **Appearance**: Elegant woman with long straight dark hair, minimal makeup, often seen in simple but high-quality clothing like cardigans and skirts
- **Personality**: Reserved, polite, occasionally invites player for tea
- **Role**: Introduces aspects of Spanish home life
- **Language Level**: Polite Spanish, clear pronunciation
- **Key Interactions**: Neighborhood information, cultural customs at home

#### Apartment Roommate
- **Name**: Alex Thompson
- **Gender**: Male
- **Age**: 28
- **Nationality**: Canadian
- **Appearance**: Athletic build with shaggy light brown hair, casual style with jeans and t-shirts often featuring Canadian or hockey logos, friendly smile, often carrying a camera or smartphone to document experiences
- **Personality**: Messy, fun-loving, night owl
- **Role**: Daily conversation partner, source of conflicts and resolutions
- **Language Level**: Mix of basic Spanish and English when frustrated
- **Key Interactions**: Sharing living space, planning weekend activities
