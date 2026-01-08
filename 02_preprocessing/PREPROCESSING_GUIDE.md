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
- **Identify**: Replies often start with "Replying to @username: " or just "@username" at the beginning of the string, or contain concatenated tags like `@user1@user2`.
- **Action**: Strip these prefixes and all mentions using a robust regex that captures the `@` and everything until the next space or another `@`.
- **Regex**: `r"@[^\s@]*"`
- **Example**: `^(@[\w.]+[: ]*|Replying to @[\w.]+[: ]*)` -> `""` (Legacy prefix handling, now subsumed by the robust regex)

### Final Dataset Preparation
To ensure the dataset is ready for model training:
- **Text Deduplication**: Drop duplicate rows based on the `comment_text` column to remove redundant signals.
- **Shuffling**: Randomly shuffle the final rows to ensure that different restaurant sentiments are mixed, avoiding bias during training batches.
- **ID Reset**: After shuffling and deduplicating, assign a new sequential `id` column (e.g., 1 to N) to provide a clean reference for each row.

---

## 2. Text Normalization

### Unified Punctuation & Spacing
- **Collapse Intensity**: Sequences of multiple identical punctuation marks (e.g., `!!!`, `???`, `...`) should be collapsed into a **single mark followed by a space**.
    - Example: `Amazing!!!` -> `Amazing! `
    - Example: `Wait... what???` -> `Wait. what? `
- **Space after Punctuation**: Ensure every punctuation mark (., !, ?, ,) is followed by a single space for better tokenization.

### Unified Emoji Mapping
We combine Intent and Topic signals into a single mapping layer. Sentiment-specific tokens ([POS]/[NEG]) are removed to focus on functional and domain drivers.

#### 1. Intent Layer
*Goal: Capture functional triggers.*
- **[APPRECIATION]**: ❤️, 🥰, 👏, 🤲, 🌹, 💐, 😂, 😍, 😁, 🤣, 🔥, 👍, ♥️, 💪, 😅, ✨, 💯, 🙏, 🤩, 😘, ☺️, 🤍, 😎, 😻, 🫡, 🫶, 🌷, 😄, 🌸, 🤗, 💋, 🌺, 🇩🇿
- **[COMPLAINT]**: 🤮, 😡, 👎, 💔, 💀, 💸, 😒, 😑, 😭, 😢, ❌, 😱, 😔, 😞, 😩, 🤢, 😫, 🥀, ☹️, 😠, 😖, 😰, 🤬
- **[INQUIRY]**: ❓, ❔, 🤔, 🧐, 👀, 📍, 📞, 🕒, 🫣
- **[RECOMMENDATION]**: 👌, 🔝, 🌟, ✨, ✅, 🥇, 👑
- **[OUT_OF_SCOPE]**: Emojis that don't fit the above categories.

#### 2. Topic Layer
*Goal: Capture domain specific keywords.*
- **[BOUFFE]**: 🥘, 🍔, 🍕, 🥙, 🥗, 🍦, 😋, 🤤, 🍜, 🍣, 🥩, 🍰, 🥐, 🥪, 🌭, 🍟, 🌮, 🦐, 🦞, 🥯, 🍯, 🍓, 🍉, 🍒, 🍋, 🍎, 🥑, 🌯, 🍗, 🍖
- **[PRICE]**: 💸, 💰, 💳, 💶, 💵
- **[TREATMENT]**: 🧑‍🍳, 👨‍🍳, 👋, 🤝, 🫂, 👋🏻
- **[SERVICE]**: 🕒, ⏳, 🛵, 🍴, 🍽️, 🏃
- **[ENDROIT]**: 📍, 🧼, 🧹, 📸, 🤳, ✨, 🌟, 🏝
- **[DELIVERY]**: 🛵, 🚚, 📦
- **[UNKNOWN]**: Emojis not mapped to a specific topic area.

---

## 3. Language & Script Filtering...

...

## 4. Intent & Topic Classification

We are using **Unified Multi-Label Classification** to identify both what the user is talking about (Topic) and why they are posting (Intent).

### Intent Categories
- **appreciation**: Generalized positive praise.
- **complaint**: Specific failure in food, price, or service.
- **inquiry**: Asking for info (location, menu).
- **recommendation**: Suggesting the place to others.
- **out of scope**: Irrelevant comments.

### Topic Categories
- **price**: Costs and value.
- **TREATMENT (personnel)**: Staff interaction.
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
| `So expensive!!!` | Collapse & Space | `So expensive! ` |
| `Good?Yes` | Add Space | `Good? Yes` |
| `Pizza 🍕🤤` | Unified Tags | `Pizza [BOUFFE]` |

---
> [!TIP]
> **Sentiment Fairness**: Never skip! If a topic is "unknown" or "general," still predict the sentiment. A comment like "I love this!" should be classified as **"General Appreciation"** with positive sentiment.
