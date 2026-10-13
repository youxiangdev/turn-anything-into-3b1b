# Newcomer questions

After a first explanation, a careful reader always comes back with questions. Every one of them
marks a place where the explanation assumed something it never said. Asking those questions
here, before anything is built, is far cheaper than answering them one at a time after the
output is finished, and it is the difference between an output people can follow and one they
have to interrogate.

So, for each part, put yourself in the seat of an intelligent person who has not read the source
and ask every question below. Write the ones that apply into the part's "Newcomer questions"
section, each with a short answer that points at the item holding it.

## How to use the bank

1. Ask every question of every part. Skip one only when it truly has no meaning for that part.
2. Answer from the sources. If answering teaches you a fact that is not yet an item, add the item.
3. If no source answers a question that matters, add a `gap` item with the question as its
   statement. Do not answer from general knowledge and present it as what the source says.
4. Keep each answer to one or two sentences. The depth is in the items; the answer is the pointer.
5. Write the questions the way a person would ask them, not as headings.

## The bank

| # | The question | A good answer has |
|---|---|---|
| 1 | **What is this, in plain words?** | One sentence and one concrete instance. No term that has not been defined. |
| 2 | **Why is it needed? What breaks without it?** | The problem, and the simpler approach that fails. |
| 3 | **What exactly happens, step by step, on one real input?** | The ordered steps with the state after each. |
| 4 | **What are the real names and numbers?** | Identifiers, defaults, limits, thresholds, sizes, timeouts. "A short hold" is not an answer; "`HOLD_MINUTES`, 10 by default" is. |
| 5 | **Where does it live, and where would I change it?** | The file, setting, command or screen. Who is allowed to change it. |
| 6 | **Who decides, and who can see it?** | Which component or person makes the decision, and which ones never see the information at all. |
| 7 | **What kinds or modes are there?** | The full list of variants and what tells them apart, not "several modes". |
| 8 | **What happens when it goes wrong?** | The failure path, what the next component receives, and the exact error text when known. |
| 9 | **Is it really like that? What about the awkward case?** | The edge case checked against a primary source: two matches instead of one, an empty input, a limit reached. |
| 10 | **How does A differ from B, exactly?** | The specific difference, and whether it is a different idea or the same idea built another way. |
| 11 | **Where does it sit in the whole flow, and what is it not responsible for?** | The neighbours on each side and the job people wrongly credit it with. |
| 12 | **So what? What does this make unnecessary, or possible?** | The consequence, and the conditions under which the older or alternative approach still wins. |
| 13 | **What does that word mean?** | A glossary entry for every term a newcomer would not know. |
| 14 | **Which ones, exactly?** | When the source says "some", "most" or "by default": the actual list, or a gap item if nobody gives it. |

## Signs that a part is not finished

- The answer to question 4 contains no identifier and no number.
- The answer to question 8 is "it handles errors".
- Question 6 was skipped. Who knows what is the most common source of confusion in any system
  with more than one actor.
- A restatement in your own words would need the phrase "somehow" or "in some way".
- The same question would have to be asked again for each implementation, and only one is answered.
