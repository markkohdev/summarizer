"""Interactive feedback system for summary refinement."""

from typing import Optional

from .llm_clients import LLMClient


FEEDBACK_TEMPLATE = """
You are refining a summary based on user feedback.

ORIGINAL SUMMARY:
{original_summary}

USER FEEDBACK:
{user_feedback}

Please revise the summary based on the feedback. Maintain the same markdown format and structure, but incorporate the requested changes.

If the user asks for:
- More detail: Add more specific information from the notes
- Less detail: Make bullets more concise while keeping key information
- Corrections: Fix any inaccuracies mentioned
- Different focus: Adjust emphasis based on the feedback

Return the revised summary in the same format as the original.
""".strip()


def get_user_feedback() -> Optional[str]:
    """Get feedback from the user interactively."""
    print("\n" + "=" * 60)
    print("FEEDBACK OPTIONS:")
    print("1. More detail - Add more specific information")
    print("2. Less detail - Make it more concise")
    print("3. Corrections - Fix inaccuracies")
    print("4. Different focus - Change emphasis or perspective")
    print("5. Custom feedback - Provide your own instructions")
    print("6. Done - Accept current summary")
    print("=" * 60)

    try:
        choice = input("\nEnter your choice (1-6): ").strip()
    except EOFError:
        return None

    if choice == "1":
        return (
            "Please add more detail and specific information to the summary. "
            "Include more context and specifics from the notes."
        )
    elif choice == "2":
        return "Please make the summary more concise. Keep the key information " "but reduce verbosity."
    elif choice == "3":
        try:
            corrections = input("What needs to be corrected? ").strip()
            if corrections:
                return f"Please correct the following: {corrections}"
        except EOFError:
            return None
    elif choice == "4":
        try:
            focus = input("What should be the new focus or emphasis? ").strip()
            if focus:
                return f"Please change the focus to emphasize: {focus}"
        except EOFError:
            return None
    elif choice == "5":
        try:
            custom = input("Provide your feedback: ").strip()
            if custom:
                return custom
        except EOFError:
            return None
    elif choice == "6":
        return None
    else:
        print("Invalid choice. Please try again.")
        return get_user_feedback()

    return None


def refine_summary(original_summary: str, user_feedback: str, client: LLMClient) -> str:
    """Refine a summary based on user feedback."""
    prompt = FEEDBACK_TEMPLATE.format(original_summary=original_summary, user_feedback=user_feedback)
    return client.complete(prompt)


def interactive_refinement_loop(initial_summary: str, client: LLMClient, max_iterations: int = 5) -> str:
    """Run an interactive loop for summary refinement."""
    current_summary = initial_summary
    iteration = 0

    while iteration < max_iterations:
        print(f"\n--- ITERATION {iteration + 1} ---")
        print(current_summary)

        feedback = get_user_feedback()
        if feedback is None:  # User chose "Done"
            break

        print("\nRefining summary based on your feedback...")
        try:
            current_summary = refine_summary(current_summary, feedback, client)
            iteration += 1
        except Exception as e:
            print(f"Error refining summary: {e}")
            print("Continuing with current version...")
            break

    if iteration >= max_iterations:
        print(f"\nReached maximum iterations ({max_iterations}). " f"Using current summary.")

    return current_summary
