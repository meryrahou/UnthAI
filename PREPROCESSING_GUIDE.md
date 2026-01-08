# NLP Preprocessing Guide: Algerian TikTok Data

This guide outlines the technical steps required to prepare the `tiktok_final_dataset.csv` for sentiment analysis and intent classification.

## 1. Structural Cleaning

### Remove GIFs & Stickers
- **Identify**: TikTok comments often contain `[GIF]` or `[Sticker]`.
- **Action**: Use regex to remove these tokens or drop rows that consist only of these strings.
- **Regex**: `r"\[GIF\]|\[Sticker\]"`

### Remove "@ & Tags Only"
- **Identify**: Comments that only tag other users.
- **Action**: If a comment consists 100% of @usernames and spacing, delete it.
- **Logic**: Count tokens; if `tag_count == total_token_count`, drop the row.

### Handle Replies & Prefixes
- **Identify**: Replies often start with "Replying to @username: " or just "@username" at the beginning of the string.
- **Action**: Strip these prefixes using regex to focus on the message intent.
- **Example**: `^(@[\w.]+[: ]*|Replying to @[\w.]+[: ]*)` -> `""`

### Final Dataset Preparation
To ensure the dataset is ready for model training:
- **Text Deduplication**: Drop duplicate rows based on the `comment_text` column to remove redundant signals.
- **Shuffling**: Randomly shuffle the final rows to ensure that different restaurant sentiments are mixed, avoiding bias during training batches.
- **ID Reset**: After shuffling and deduplicating, assign a new sequential `id` column (e.g., 1 to N) to provide a clean reference for each row.

---

## 2. Text Normalization

### Punctuation Intensity (`...`, `???`, `!!!`)
- **Strategy**: Do not delete! These are major sentiment signals indicating intensity.
- **Normalization**: Map sequences like `!!!!!!!` or `??????` to specific tokens like `[EXTREME_INTENSITY]` or simply `[!]`. This preserves the signal while reducing vocabulary size.

### Emojis: Tiered Task-Specific Mapping
To maximize signal across our three classification tasks, we use different mapping strategies depending on the objective:

#### 1. Sentiment Mode
*Goal: Capture emotional valence.*
- **[POS]**: ❤️, 🥰, 😍, 🔥, 😋, 😂, 👏, 💯, 👍, 😁, 🤩, 😊, 🥳, 💪, 🤲, 🌹, 💐, 💎, 🇩🇿
- **[NEG]**: 🤮, 😡, 👎, 💔, 💀, 💸, 😭, 😢, 😒, 😑, 😱

#### 2. Intent Mode
*Goal: Capture functional triggers.*
- **[APPRECIATION]**: ❤️, 🥰, 😂, 👏, 🤲, 🌹, 💐
- **[COMPLAINT]**: 🤮, 😡, 👎, 💔, 💀, 💸, 😒, 😑
- **[INQUIRY]**: ❓, ❔, 🤔, 🧐, 👀, 📍, 📞, 🕒
- **[RECOMMENDATION]**: 👌, 🔝, 🌟, ✨, ✅, 🥇, 👑
- **[OUT_OF_SCOPE]**: Emojis that don't fit the above (e.g., random animals, flags other than 🇩🇿).

#### 3. Topic Mode
*Goal: Capture domain specific keywords.*
- **[BOUFFE]**: 🥘, 🍔, 🍕, 🥙, 🥗, 🍦, 😋, 🤤, 🍜, 🍣, 🥩
- **[PRICE]**: 💸, 💰, 💳, 💶, 💵
- **[TREATMENT]**: 🧑‍🍳, 👨‍🍳, 👋, 🤝, 🫂
- **[SERVICE]**: 🕒, ⏳, 🛵, 🍴, 🍽️
- **[ENDROIT]**: 📍, 🧼, 🧹, 📸, 🤳, ✨, 🌟, 🏝
- **[DELIVERY]**: 🛵, 🚚, 📦
- **[UNKNOWN]**: Emojis not mapped to a specific topic area.

---

## 3. Language & Script Filtering...

...

## 4. Intent & Multimodal Classification

We are moving past simple sentiment into **Intent-Based Multimodal Classification**.

### Intent Categories
- **appreciation**: Generalized positive praise without detailed specifics.
- **complaint**: Expressing a specific failure in food, price, or service.
- **inquiry**: Asking for info (location, price list, menu items).
- **recommendation**: Actively suggesting the place to others or warning them away.
- **out of scope**: Irrelevant or general comments.

### Topic Categories
- **price**: Costs and value.
- **TREATMENT (personnel)**: Quality of staff interaction.
- **bouffe**: Food and drink quality.
- **service (waiting time)**: Efficiency and speed.
- **endroit (propreté)**: Cleanliness and vibes.
- **delivery**: Home delivery services.
- **unknown**: Topic not clearly identified.

---

## 5. Preprocessing Summary Table

| Comment Example | Action | Final Format |
| :--- | :--- | :--- |
| `[GIF]` | Drop Row | (NULL) |
| `@mery Check it out` | Remove tag | `Check it out` |
| `Amazing 🔥😍` | Map to token | `Amazing [POS_EMOJI]` |
| `Waiters were fast` | Factual praise | `Intent=Review, Sentiment=Neutral` |
| `So expensive 💸!!!` | Map flags | `So expensive [NEG_EMOJI] [INTENSE]` |

---
> [!TIP]
> **Sentiment Fairness**: Never skip! If a topic is "unknown" or "general," still predict the sentiment. A comment like "I love this!" should be classified as **"General Appreciation"** with positive sentiment.
