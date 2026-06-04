import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sonicloud_harness.ad_policy import (
    AdContext,
    AdEvent,
    AdFormat,
    AdTimingPolicy,
    FakeAdAdapter,
    ScreenType,
)


class AdTimingPolicyTest(unittest.TestCase):
    def test_blocks_interstitial_before_task_completion(self) -> None:
        policy = AdTimingPolicy()
        decision = policy.decide(
            AdContext(
                event=AdEvent.TASK_STARTED,
                screen=ScreenType.INPUT,
                ad_format=AdFormat.INTERSTITIAL,
                now_seconds=300,
                user_action_completed=False,
            )
        )

        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "block_screen_input")

    def test_allows_interstitial_after_result_saved(self) -> None:
        policy = AdTimingPolicy()
        decision = policy.decide(
            AdContext(
                event=AdEvent.RESULT_SAVED,
                screen=ScreenType.RESULT,
                ad_format=AdFormat.INTERSTITIAL,
                now_seconds=300,
                last_ad_seconds=None,
                user_action_completed=True,
            )
        )

        self.assertTrue(decision.allowed)
        self.assertEqual(decision.reason, "allow")

    def test_blocks_cooldown(self) -> None:
        policy = AdTimingPolicy(min_interval_seconds=180)
        decision = policy.decide(
            AdContext(
                event=AdEvent.RESULT_SAVED,
                screen=ScreenType.RESULT,
                ad_format=AdFormat.INTERSTITIAL,
                now_seconds=300,
                last_ad_seconds=250,
                user_action_completed=True,
            )
        )

        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "block_cooldown")

    def test_fake_adapter_records_shown_and_blocked(self) -> None:
        adapter = FakeAdAdapter()
        allowed = adapter.maybe_show(
            AdContext(
                event=AdEvent.RESULT_SAVED,
                screen=ScreenType.RESULT,
                ad_format=AdFormat.INTERSTITIAL,
                now_seconds=300,
                user_action_completed=True,
            )
        )
        blocked = adapter.maybe_show(
            AdContext(
                event=AdEvent.TASK_STARTED,
                screen=ScreenType.PROCESSING,
                ad_format=AdFormat.INTERSTITIAL,
                now_seconds=301,
            )
        )

        self.assertTrue(allowed.allowed)
        self.assertFalse(blocked.allowed)
        self.assertEqual(len(adapter.shown), 1)
        self.assertEqual(len(adapter.blocked), 1)


if __name__ == "__main__":
    unittest.main()
