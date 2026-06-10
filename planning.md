# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
Yugioh Deck Building, Strategies, and Counters — a searchable guide covering how to build competitive decks, understand the current meta, counter popular strategies, and make smart card choices.

This guide covers deck building strategies, meta analysis, and counter strategies for the Yu-Gi-Oh! Trading Card Game. This knowledge is hard to find in one place because it's scattered across wikis, Reddit threads, tournament sites, and competitive forums with constantly shifting metas. The system can answer questions like: 'What are the best hand traps to counter Snake-Eye?', 'How do I build a budget competitive deck?', and 'What's the best going-second strategy in the current meta?

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Yugipedia - Archetypes | Basic rundown of Yu-Gi-Oh! archetypes and the full list of them. | https://yugipedia.com/wiki/Archetype |

| 2 | Game8 - Yu-Gi-Oh! Master Duel Beginner's Guide: Tips For Starting Out | A beginner's guide covering core mechanics, starting tips, and deck building fundamentals for Master Duel. | https://game8.co/games/Yu-Gi-Oh-Master-Duel/archives/354362 |

| 3 | r/yugioh - Q&A and Ruling Megathread - June 08, 2026 | A thread based on up to date Yugioh rulings. | https://www.reddit.com/r/yugioh/comments/1tzx4vi/qa_and_ruling_megathread_june_08_2026/ |

| 4 | MasterDuelMeta - Combos & Counters | A page where players share their YuGiOh combos of their respective archetypes. | https://www.masterduelmeta.com/combos-and-counters#counters |

| 5 | Yugipedia - Hand Traps | Full list of hand trap cards with rulings, usage notes, and interaction breakdowns. Best single page for hand trap strategy. | https://yugipedia.com/wiki/Hand_trap |

| 6 | MasterDuelMeta - A Re-Introductory Guide to Modern Yu-Gi-Oh! | A returning player guide covering modern mechanics, retro staples, and deck recommendations. | https://www.masterduelmeta.com/articles/guides/returning-player-ryu |

| 7 | YGOPRODeck - The Repeat Offenders of Yu-Gi-Oh's Forbidden & Limited List Part 4 | Analysis of cards that have repeatedly appeared on the Forbidden & Limited list and why. | https://ygoprodeck.com/article/the-repeat-offenders-of-yu-gi-oh-s-forbidden-amp-limited-list-part-4-302873/ |

| 8 | MasterDuelMeta - Guides | A page dedicated to various archetype guides made and published by players. | https://www.masterduelmeta.com/guides |

| 9 | Yu-Gi-Oh! Rulebook | The official rules guide to Yu-Gi-Oh! | https://img.yugioh-card.com/en/downloads/rulebook/SD_RuleBook_EN_10.pdf |

| 10 | r/masterduel - Guides/Combos + Questions and Help MEGATHREAD! | Megathread dedicated for players to share combos and ask questions about specific card interactions. | https://www.reddit.com/r/masterduel/comments/sve5fr/guidescombos_questions_and_help_megathread/ |


---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**
400 tokens, semantic
**Overlap:**
50 tokens
**Reasoning:**
My sources consist of variety of long-form guides. I believe 400 chunks is enough to capture a full meaningfull strategy or card interactions in one piece but also small enough to keep it from being too overcomplicated. A 50 token overlap prevents strategy advice from being cut mid-explanation at chunk boundaries without introducing 
too much redundancy. 
---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**
all-MiniLM-L6-v2

**Top-k:**
4 chunks will be retrieved per query
**Production tradeoff reflection:**
If this were a real deployment I would prioritize on speed and accuracy over the context length. The user is most likely using the model during a game so faster and more accurate response means a better experience for the user. To compensate for the shorter context length, I would make sure my chunks are tightly focused on one topic so the AI can still provide useful answers without needed to explain unless asked. Also some card names are too long, it would be great to shorten them.
---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 |What is the best moment to use hand traps on Sky Strikers?|  The best moment hand trap would be Droll & Lock bird after one card draw. Another moment would be using Ash Blossom & Joyous Spring / Ghost Belle & Haunted Mansion on Sky Striker Ace = Zero's tribute effect. |
| 2 |What happens when I chain "Called by the Grave" to my opponent's "Monster Reborn" target? | "Called by the Grave" is on a higher chain link meaning that the targetting monster will get banished and "Monster Reborn"'s effect will not go through. 
| 3 |What is an omni negate?| An omni negate a card effect that's capable of negating any card effect that activates. |
| 4 | What is a synchro summon?|  A synchro summon is summoing an extra deck Synchro monster by using the required monsters, levels, and tuners on the field. |
| 5 | How many cards maximum can I have in the main deck?| You can have the maximum of 60 cards in the main deck and the minimum of 40 cards. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. The AI could become inconsistent or mention a combo that is illegal to occur in a real game. 

2. Chunks can possibly split key information depending on what deck you or your opponent is using. Some combos can stretch for longer than the token limit I provded to the AI. 

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->
|Ingestion: Yugipedia, YGOProdeck, Master Duel Meta, Reddit threads, Rulebook PDF|

|
v

|Chunking: Fixed 400 tokens with 50 overlap. Semantic chunking strategy|

|
v

|Embedding: sentence-transformers (all-MiniLM-L6-v2) + ChromaDB |

|
v

|Retrieval: ChromaDB similarity search, top-k = 4 |

|
v

|Generation: Groq (llama-3.3-70b-versatile) |
---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->
I plan to utilize Claude to to write a function that queries ChromaDB and returns the top 4 most relevant chunks. Will double check with my sample questions and expect relevant response for each of my questions. 

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
