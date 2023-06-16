#!/usr/bin/env python3


from dialogue.dialogue_summarizer import DialogueSummarizer


def main():
    # Given a dialogue, this example relies on the class DialogueSummarizer to get a response from
    # an AI model, a response that should contain the summary of the messages passed.

    messages = []

    dialogue_line = "The Captain: Neither of you can read a map? How have we survived for this long?"
    messages.append(
        {
            "role": "user",
            "content": dialogue_line,
        }
    )

    dialogue_line = "Bimbo: Honestly, Captain, these woods ain't like any I've seen. All the trees look the same. And under this dim light, "
    dialogue_line += "I can't make head or tail of this damn map."
    messages.append(
        {
            "role": "user",
            "content": dialogue_line,
        }
    )

    dialogue_line = "Kutinaira: Oh, don't worry dear Captain. Even if we encounter orcs, we have your strong, virile body to protect us."
    messages.append(
        {
            "role": "user",
            "content": dialogue_line,
        }
    )

    dialogue_line = "The Captain: You think that the orcs would be so sexually enthralled by my virile body that they would forsake all notion of self-defense?"
    messages.append(
        {
            "role": "user",
            "content": dialogue_line,
        }
    )

    dialogue_line = "Bimbo: (Laughs nervously) If that were the solution, these forests would be peaceful. Orcs are stubborn, and dumb… too dumb to let go of hostility."
    messages.append(
        {
            "role": "user",
            "content": dialogue_line,
        }
    )

    dialogue_line = "Kutinaira: (Purrs) You ought not to underestimate yourself, Captain. The sight of your rippling muscles would make anyone drop their weapons. "
    dialogue_line += "Surely, surrendering to you would be a far better fate."
    messages.append(
        {
            "role": "user",
            "content": dialogue_line,
        }
    )

    dialogue_line = "The Captain: (Strokes his chin thoughtfully) Would orc females be into mommy fantasies?"
    messages.append(
        {
            "role": "user",
            "content": dialogue_line,
        }
    )

    dialogue_line = (
        "Bimbo: (Turns pale and stammers) C-Captain, that's… quite a strange question…"
    )
    messages.append(
        {
            "role": "user",
            "content": dialogue_line,
        }
    )

    dialogue_line = "Kutinaira: (Laughs loudly and claps her hands) Oh, such is the humor of the humans! Now that's a sight, an orc swooning over "
    dialogue_line += "you like a mother… How kinky, and how horrible."
    messages.append(
        {
            "role": "user",
            "content": dialogue_line,
        }
    )

    dialogue_line = "The Captain: (Crosses his arms) Horrible, huh? I didn't shame your kink that one time you came mid-battle because a minotaur was choking you."
    messages.append(
        {
            "role": "user",
            "content": dialogue_line,
        }
    )

    dialogue_line = "Bimbo: (Looks away, turning a deep shade of red)"
    messages.append(
        {
            "role": "user",
            "content": dialogue_line,
        }
    )

    dialogue_line = "Kutinaira: (Chuckles) Ah, Captain, you remember the most endearing of times. But do remember, my dear, my kinks and your… propositions of orcs, "
    dialogue_line += "they are not quite the same thing. Ah, the diversity of life's pleasures… it is simply delicious!"
    messages.append(
        {
            "role": "user",
            "content": dialogue_line,
        }
    )

    dialogue_line = "The Captain: Kutinaira, one of these days we're going to die for real. We're skirting the edge of debauchery here. "
    dialogue_line += "I mean, I go out of my way to hunt down demonettes because I can't have enough of those forked tongues and their horns. "
    dialogue_line += (
        "Oh, and those glorious claws. My back looks like I've been flogged for years!"
    )
    messages.append(
        {
            "role": "user",
            "content": dialogue_line,
        }
    )

    dialogue_line = "Bimbo: (Gulps audibly, clearly uncomfortable with how the conversation is turning)"
    messages.append(
        {
            "role": "user",
            "content": dialogue_line,
        }
    )

    dialogue_line = "Kutinaira: (Laughs a throaty laugh) What a delightful image you paint, Captain! "
    dialogue_line += "You are certainly an adventurer of more than just landscapes and dungeons. But do remember, death is a part of this life we lead, "
    dialogue_line += (
        "and if I were to meet my end, I'd rather do so in a state of divine pleasure."
    )
    messages.append(
        {
            "role": "user",
            "content": dialogue_line,
        }
    )

    dialogue_line = "The Captain: (Nodding) You know, Kutinaira, I used to think of you as little more than an old reprobate who hides a "
    dialogue_line += "legion's worth of sexually transmitted diseases, but you're actually quite the philosopher, aren't you?"
    messages.append(
        {
            "role": "user",
            "content": dialogue_line,
        }
    )

    dialogue_line = "Bimbo: (Speaks timidly) You two sure know how to keep a conversation… uh, interesting."
    messages.append(
        {
            "role": "user",
            "content": dialogue_line,
        }
    )

    dialogue_line = "Kutinaira: (Giggles, flicking her hair over her shoulder) Oh, Captain, compliments from your mouth are as sweet as honeyed wine. "
    dialogue_line += "We all hide our depths beneath what we present, do we not? Now, let's indulge in the philosophy of finding our path again… "
    dialogue_line += "Unless, of course, you wish to discuss more… stimulating ideas."
    messages.append(
        {
            "role": "user",
            "content": dialogue_line,
        }
    )

    dialogue_line = "The Captain: Yeah, let's find those goblins and exterminate their whole families. "
    dialogue_line += "Once we wander out of that hole and take a bath in a river, let's discuss in private some stimulating ideas."
    messages.append(
        {
            "role": "user",
            "content": dialogue_line,
        }
    )

    dialogue_summarizer = DialogueSummarizer(messages)

    dialogue_summary = dialogue_summarizer.summarize()

    print(dialogue_summary["choices"][0]["message"])


if __name__ == "__main__":
    main()
