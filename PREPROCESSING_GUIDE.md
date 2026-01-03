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

---

## 2. Text Normalization

### Punctuation Intensity (`...`, `???`, `!!!`)
- **Strategy**: Do not delete! These are major sentiment signals indicating intensity.
- **Normalization**: Map sequences like `!!!!!!!` or `??????` to specific tokens like `[EXTREME_INTENSITY]` or simply `[!]`. This preserves the signal while reducing vocabulary size.

### Emojis: Selective Mapping & Noise Reduction
We will adopt a **selective mapping** strategy based on the restaurant/food theme:
- **Action**: Map high-signal emojis to tokens and **delete all other emojis** (e.g., flags, random objects, unrelated symbols).

| Category | Emojis | Token |
| :--- | :--- | :--- |
| **Positive** | ❤️, 😍, 🔥, 😋, 🤤, 👌, 💯, ✨, 🌟, 🔝, 👍, 👏, 🥰, 🥘, 🍔, 🍕, 🥙, 🥗, 🌮, 🍗, 🍡, 🍱, 🥧, 🍰, 🍦, 🥂 | `[POS_EMOJI]` |
| **Negative** | 🤮, 🤢, 😡, 👎, 💸, 📉, 🚫, 💀, 💩, 🤡, 🙄, 😤, 🤬, 🚮, 💔 | `[NEG_EMOJI]` |
| **Neutral** | 📍, 📞, 🕒, 🚗, 🛵, 🍴, ☕, 🥤, 🍨, 🥖, 🧂 | `[NEUT_EMOJI]` |

---

## 3. Language & Script Filtering

### Script Enforcement
Since your target is Algeria, we keep only **Arabic** and **Latin** (French/English/Arabizi) characters.
- **Action**: Use a library like `langid` or character set checks to remove comments containing non-target scripts (Cyrillic, Asian scripts, etc.).
- **Symbol Check**: Remove comments consisting *only* of symbols/punctuation with no actual text.

---

## 4. Intent & Multimodal Classification

We are moving past simple sentiment into **Intent-Based Multimodal Classification**.

### The Objective
Identify the **Intent** of the user. This identifies the *driver* of the feedback, providing more actionable insights.

### Multimodal Layers
1. **Text Layer**: BERT/MARBERT embeddings for semantic meaning.
2. **Emoji Layer**: Categorized tokens (`[POS_EMOJI]`, etc.) to weight emotional intent.
3. **Punctuation Layer**: Mapping intensity signals to flags like `[INTENSE]`.

### Intent Categories
- **Review**: Sharing a personal experience or opinion on a visit.
- **Inquiry**: Asking for info (location, price list, menu items).
- **Recommendation**: Actively suggesting the place to others or warning them away.
- **Complaint**: Expressing a specific failure in food, price, or service.
- **Appreciation**: Generalized positive praise without detailed specifics.

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
