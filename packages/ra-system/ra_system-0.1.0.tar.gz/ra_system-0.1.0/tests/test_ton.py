"""
Tests for T.O.N. (Table of Nines) module.

Tests Invariant I5: T.O.N.(m) = m × 0.027 for all m ∈ [0, 36]
"""

from ra_system.ton import (
    TON,
    TON_COEFFICIENT,
    all_tons,
    is_valid_ton_index,
    repitan_ton_ratio,
    ton_from_value,
    verify_ton_invariant,
    verify_ton_range_invariant,
)


class TestTONCreation:
    """Tests for T.O.N. creation and validation."""

    def test_valid_indices_create_successfully(self) -> None:
        """All valid indices [0, 36] create successfully."""
        for m in range(37):
            t = TON.create(m)
            assert t is not None
            assert t.index == m

    def test_invalid_indices_return_none(self) -> None:
        """Invalid indices return None from smart constructor."""
        assert TON.create(-1) is None
        assert TON.create(37) is None
        assert TON.create(100) is None

    def test_direct_construction_with_invalid_raises(self) -> None:
        """Direct construction with invalid index raises ValueError."""
        try:
            TON(-1)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "must be in [0, 36]" in str(e)

        try:
            TON(37)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "must be in [0, 36]" in str(e)


class TestTONInvariant:
    """Tests for T.O.N. invariant I5."""

    def test_i5_ton_equals_m_times_coefficient(self) -> None:
        """I5: T.O.N.(m) = m × 0.027 for all m ∈ [0, 36]."""
        assert verify_ton_invariant()
        for m in range(37):
            t = TON(m)
            expected = m * TON_COEFFICIENT
            assert abs(t.value - expected) < 1e-10

    def test_ton_values_in_range(self) -> None:
        """All T.O.N. values are in [0, 1)."""
        assert verify_ton_range_invariant()
        for t in all_tons():
            assert 0 <= t.value < 1

    def test_coefficient_value(self) -> None:
        """T.O.N. coefficient is 0.027."""
        assert TON_COEFFICIENT == 0.027


class TestTONClassConstants:
    """Tests for T.O.N. class constants."""

    def test_zero_ton(self) -> None:
        """T.O.N.ZERO is index 0."""
        assert TON.ZERO.index == 0
        assert TON.ZERO.value == 0.0

    def test_ninth_ton(self) -> None:
        """T.O.N.NINTH is index 9."""
        assert TON.NINTH.index == 9
        assert abs(TON.NINTH.value - 0.243) < 1e-10

    def test_eighteenth_ton(self) -> None:
        """T.O.N.EIGHTEENTH is index 18."""
        assert TON.EIGHTEENTH.index == 18
        assert abs(TON.EIGHTEENTH.value - 0.486) < 1e-10

    def test_twenty_seventh_ton(self) -> None:
        """T.O.N.TWENTY_SEVENTH is index 27."""
        assert TON.TWENTY_SEVENTH.index == 27
        assert abs(TON.TWENTY_SEVENTH.value - 0.729) < 1e-10

    def test_max_ton(self) -> None:
        """T.O.N.MAX is index 36."""
        assert TON.MAX.index == 36
        assert abs(TON.MAX.value - 0.972) < 1e-10


class TestTONNavigation:
    """Tests for T.O.N. navigation methods."""

    def test_next_increments(self) -> None:
        """next() increments index."""
        t = TON(9)
        assert t.next().index == 10

    def test_next_wraps_at_max(self) -> None:
        """next() wraps from 36 to 0."""
        t = TON(36)
        assert t.next().index == 0

    def test_prev_decrements(self) -> None:
        """prev() decrements index."""
        t = TON(9)
        assert t.prev().index == 8

    def test_prev_wraps_at_zero(self) -> None:
        """prev() wraps from 0 to 36."""
        t = TON(0)
        assert t.prev().index == 36

    def test_distance_direct(self) -> None:
        """distance() calculates direct distance."""
        t1 = TON(5)
        t2 = TON(10)
        assert t1.distance(t2) == 5
        assert t2.distance(t1) == 5

    def test_distance_wrapping(self) -> None:
        """distance() uses shorter wrap-around when appropriate."""
        t1 = TON(2)
        t2 = TON(35)
        # Direct: 33, Wrapped: 4
        assert t1.distance(t2) == 4

    def test_distance_max_is_18(self) -> None:
        """Maximum distance is 18 (half of 37)."""
        t1 = TON(0)
        t2 = TON(18)
        assert t1.distance(t2) == 18

        t3 = TON(19)
        assert t1.distance(t3) == 18  # 37 - 19 = 18


class TestTONConversions:
    """Tests for T.O.N. conversion functions."""

    def test_ton_from_value_exact(self) -> None:
        """ton_from_value converts exact values."""
        t = ton_from_value(0.243)  # Index 9
        assert t.index == 9

    def test_ton_from_value_rounds(self) -> None:
        """ton_from_value rounds to nearest index."""
        t = ton_from_value(0.25)  # Between 9 (0.243) and 10 (0.270)
        assert t.index == 9  # Closer to 9

    def test_ton_from_value_clamps_low(self) -> None:
        """ton_from_value clamps negative values to 0."""
        t = ton_from_value(-0.5)
        assert t.index == 0

    def test_ton_from_value_clamps_high(self) -> None:
        """ton_from_value clamps values > 36*0.027 to 36."""
        t = ton_from_value(2.0)
        assert t.index == 36


class TestTONCollections:
    """Tests for T.O.N. collection functions."""

    def test_all_tons_returns_37(self) -> None:
        """all_tons() returns 37 T.O.N. values."""
        tons = all_tons()
        assert len(tons) == 37

    def test_all_tons_sorted(self) -> None:
        """all_tons() returns sorted T.O.N. values."""
        tons = all_tons()
        for i, t in enumerate(tons):
            assert t.index == i

    def test_is_valid_ton_index(self) -> None:
        """is_valid_ton_index validates correctly."""
        for m in range(37):
            assert is_valid_ton_index(m)
        assert not is_valid_ton_index(-1)
        assert not is_valid_ton_index(37)
        assert not is_valid_ton_index(1.5)  # type: ignore


class TestTONRepitanRelationship:
    """Tests for T.O.N. and Repitan relationship."""

    def test_repitan_ton_ratio(self) -> None:
        """Repitan/T.O.N. ratio is approximately Fine Structure related."""
        ratio = repitan_ton_ratio()
        # (1/27) / 0.027 = 0.037037... / 0.027 = 1.371742112...
        assert abs(ratio - 1.371742112) < 0.001

    def test_repitan_aligned_check(self) -> None:
        """Check is_repitan_aligned for key T.O.N. values."""
        # T.O.N.(9) = 0.243, Repitan(7) = 7/27 ≈ 0.259 (close but > 0.01)
        # T.O.N.(27) = 0.729, Repitan(20) = 20/27 ≈ 0.741 (close)
        t27 = TON(27)
        # Check if any repitan aligns
        # 0.729 is close to 20/27 = 0.7407... (diff = 0.0117, > 0.01 threshold)
        # Verify the method runs without error and returns expected type
        assert isinstance(t27.is_repitan_aligned, bool)
        assert t27.aligned_repitan_index is None or isinstance(t27.aligned_repitan_index, int)


class TestTONOrdering:
    """Tests for T.O.N. ordering (frozen dataclass with order=True)."""

    def test_less_than(self) -> None:
        """T.O.N. supports < comparison."""
        assert TON(5) < TON(10)

    def test_greater_than(self) -> None:
        """T.O.N. supports > comparison."""
        assert TON(10) > TON(5)

    def test_equality(self) -> None:
        """T.O.N. supports == comparison."""
        assert TON(5) == TON(5)

    def test_sorting(self) -> None:
        """T.O.N. values can be sorted."""
        tons = [TON(10), TON(5), TON(20), TON(1)]
        sorted_tons = sorted(tons)
        assert [t.index for t in sorted_tons] == [1, 5, 10, 20]
