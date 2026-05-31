# Visual Novel Story Structure (Spanish Learner)

## Core Framework

- Linear progression through scenes
- Each scene features one character with the player
- Key decision points that lead to specific branches
- All interactions flow naturally from one to the next

## NodeState

When a current dialog node is set it becomes a state with:

- `speaker`
- `response`

## Story Data Structure Example

This is an example of a story scene in JSON format that is stored in the `outputs/scenes/` directory.

```json
{
    "id": "scene001",
    "title": "Bienvenido a Madrid",
    "location_id": "apartment",
    "character_id": "alex",
    "dialog": {
        "000": {
            "speaker": "player",
            "spanish": "Te despiertas en tu nuevo apartamento en Madrid. La luz de la mañana entra por las persianas mientras escuchas ruido en la cocina.",
            "english": "You wake up in your new apartment in Madrid. Morning light streams through the blinds as you hear someone in the kitchen.",
            "default_next_id": "001"
        },
        "001": {
            "speaker": "alex",
            "spanish": "¡Hola! ¿Ya te despertaste?",
            "english": "Hey! You're awake?",
            "choices": [
                {
                    "english": "Good morning. You must be Alex?",
                    "spanish": "Buenos días. ¿Tú eres Alex?",
                    "next_id": "002"
                }
            ]
        },
        "030": {
            "speaker": "alex",
            "spanish": "Hasta luego, no olvides pasar por Correos.",
            "english": "See you later, remember to visit the post office!",
            "next_scene_id": "scene003"
        }
    }
}
```

- `speaker` is always the player or another character.
- There is no separate narrator; the player's inner monologue acts like narration when needed.
- If there are no `choices`, `default_next_id` transitions to the next node.
- `choices` are always from the player's perspective and can include an optional `response` block.

Sometimes a choice shows a short response but still follows the `default_next_id`.

```json
{
  "id": "scene002",
  "dialog": {
    "000": {
      "speaker": "alex",
      "spanish": "¡Buenos días! ¿Ya estás listo para tu primera clase?",
      "english": "Good morning! Ready for your first class?",
      "default_next_id": "001",
      "choices": [
        {
          "english": "Yes, I'm excited!",
          "spanish": "Sí, estoy emocionado.",
          "response": {
            "speaker": "alex",
            "spanish": "¡Genial! Te llevaré al centro de idiomas.",
            "english": "Great! I'll take you to the language center."
          }
        }
      ]
    }
  }
}
```

## Story Structure

### Chapter 1: First Day in Spain

1. **Scene 1**: Player wakes up in their apartment; Alex (roommate) welcomes them to Madrid
2. **Scene 2**: Alex gives basic information about the neighborhood and the language academy
3. **Scene 3**: Player arrives at the language school, meets Profesora García
4. **Scene 4**: First basic Spanish lesson with Profesora García
5. **Scene 5**: Homework assignment: visit Correos (post office) to mail a form

### Chapter 2: Getting Oriented

1. **Scene 1**: Visit to Correos, meeting Señor Fernández
2. **Scene 2**: Language challenge with forms (player practices formal Spanish)
3. **Scene 3**: Return to apartment, Alex suggests visiting a café for practice
4. **Scene 4**: Visit to café, meeting María

**Branch Point 1**: How you respond to María's question about what you want to focus on

- Option A: Academic focus -> Study Path
- Option B: Cultural understanding -> Culture Path
- Option C: Daily conversation skills -> Practical Path

### Study Path (Branch A)

1. **Scene 1**: María introduces you to Carlos at the café
2. **Scene 2**: Study session with Carlos at the language school
3. **Scene 3**: Advanced lesson with Profesora García
4. **Scene 4**: Meeting Ana at the school library
5. **Scene 5**: Grammar challenge with Ana

**Branch Point 2A**: Your approach to language learning

- Option A1: Text-focused study -> Reading/Writing Ending
- Option A2: Conversation practice -> Speaking/Listening Ending

### Culture Path (Branch B)

1. **Scene 1**: María shares cultural insights during the café break
2. **Scene 2**: Meeting Isabel at her apartment for tea
3. **Scene 3**: Cultural lesson with Isabel (traditions, fiestas)
4. **Scene 4**: Visit to the local tienda, discussion with Javier about customs
5. **Scene 5**: Cultural practice exercises with Profesora García

**Branch Point 2B**: How you engage with Spanish culture

- Option B1: Traditional customs -> Traditional Ending
- Option B2: Contemporary urban culture -> Contemporary Ending

### Practical Path (Branch C)

1. **Scene 1**: Alex shows practical Spanish phrases at the apartment
2. **Scene 2**: Shopping practice at Javier's tienda
3. **Scene 3**: Practical conversation at café with María
4. **Scene 4**: Real-life application exercises with Profesora García
5. **Scene 5**: Final practical challenge at Correos with Señor Fernández

**Branch Point 2C**: Your approach to daily communication

- Option C1: Independent problem-solving -> Self-Reliance Ending
- Option C2: Community assistance -> Social Connection Ending

### Final Chapter: Language Assessment

Each path concludes with a final assessment at the language school with Profesora García, with content varying based on the chosen path.

## Endings Overview

### Study Path Endings

- **Reading/Writing Ending**: Player excels in written Spanish and passes an intermediate-level exam, such as DELE A2/B1 equivalent
- **Speaking/Listening Ending**: Player develops strong conversational skills and can navigate complex discussions

### Culture Path Endings

- **Traditional Ending**: Player gains deep appreciation for Spanish traditions and local customs
- **Contemporary Ending**: Player becomes fluent in modern expressions and urban cultural references

### Practical Path Endings

- **Self-Reliance Ending**: Player can confidently handle daily tasks and errands in Spanish
- **Social Connection Ending**: Player builds a supportive local network through language practice

## Language Learning Integration

Each scene includes:

- **Relevant Vocabulary**: Words and phrases specific to the location and situation, such as `Correos`, `tienda`, and `metro`
- **Grammar Points**: New structures introduced through character dialog, such as present, preterite, imperfect, pronouns, formal vs informal
- **Cultural Notes**: Insights into Spanish customs, greetings, and etiquette
- **Practice Exercises**: Interactive language challenges with feedback, such as fill-in-the-blanks, choose the correct register, and roleplay responses

## Character-Specific Language Focus

- **Profesora García**: Formal Spanish, grammar explanations, academic vocabulary
- **María**: Casual conversation, colloquial expressions, café and social phrases
- **Señor Fernández**: Formal interactions, bureaucratic language, written forms
- **Carlos**: Study techniques, grammar drills, reading comprehension
- **Ana**: Vocabulary expansion, memorization strategies
- **Javier**: Everyday shopping vocabulary, numbers, bargaining phrases
- **Isabel**: Polite language, cultural terminology, traditional expressions
- **Alex Thompson**: Daily life conversation, roommate and housing vocabulary, basic needs
