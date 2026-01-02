"""
Integration tests for Ra System invariants.

Tests all 17 invariants from ra_integration_spec.md Section 6.
"""

from ra_system.constants import (
    ANKH,
    BLUE_PI,
    FINE_STRUCTURE,
    GREEN_PHI,
    GREEN_PI,
    H_BAR,
    HUNAB,
    OMEGA,
    RED_PI,
    verify_ankh_invariant,
    verify_fine_structure_invariant,
    verify_hbar_invariant,
)
from ra_system.gates import (
    COHERENCE_CEILING,
    COHERENCE_FLOOR,
    access_level,
    verify_coherence_bounds,
    verify_coherence_floor,
)
from ra_system.omega import (
    OmegaFormat,
    green_to_omega_major,
    green_to_omega_minor,
    harmonic_from_omega,
    verify_all_omega_roundtrips,
    verify_omega_range,
)
from ra_system.rac import (
    RacLevel,
    all_rac_levels,
    rac_value,
    verify_rac1_derivation,
    verify_rac_ordering,
    verify_rac_range,
)
from ra_system.repitans import (
    Repitan,
    all_repitans,
    repitan_from_theta,
    verify_repitan_invariant,
    verify_repitan_range_invariant,
)
from ra_system.spherical import (
    RaCoordinate,
    denormalize_radius,
    normalize_radius,
    theta_from_repitan,
    verify_omega_indices,
)
from ra_system.ton import (
    TON_COEFFICIENT,
    all_tons,
    verify_ton_invariant,
    verify_ton_range_invariant,
)

# =============================================================================
# Constant Invariants (I1-I6)
# =============================================================================


class TestConstantInvariants:
    """Tests for constant invariants I1-I6."""

    def test_i1_ankh_equals_red_pi_times_green_phi(self) -> None:
        """I1: Ankh = π_red × φ_green."""
        computed = RED_PI * GREEN_PHI
        assert abs(ANKH - computed) < 0.0001
        assert verify_ankh_invariant()

    def test_i2_rac1_equals_ankh_div_8(self) -> None:
        """I2: RAC₁ = Ankh / 8."""
        computed = ANKH / 8
        assert abs(rac_value(RacLevel.RAC1) - computed) < 0.0001
        assert verify_rac1_derivation()

    def test_i3_hbar_equals_hunab_div_omega(self) -> None:
        """I3: H-Bar = Hunab / Ω."""
        computed = HUNAB / OMEGA
        assert abs(H_BAR - computed) < 0.0001
        assert verify_hbar_invariant()

    def test_i4_repitan_equals_n_div_27(self) -> None:
        """I4: Repitan(n) = n / 27 for all n ∈ [1, 27]."""
        assert verify_repitan_invariant()
        for n in range(1, 28):
            r = Repitan.create(n)
            assert r is not None
            assert abs(r.value - n / 27) < 1e-10

    def test_i5_ton_equals_m_times_0027(self) -> None:
        """I5: T.O.N.(m) = m × 0.027 for all m ∈ [0, 36]."""
        assert verify_ton_invariant()
        assert verify_ton_range_invariant()
        for t in all_tons():
            expected = t.index * TON_COEFFICIENT
            assert abs(t.value - expected) < 1e-10
            assert 0 <= t.value < 1

    def test_i6_fine_structure_equals_repitan1_squared(self) -> None:
        """I6: Fine Structure = Repitan(1)² = 0.0013717421."""
        r1 = Repitan.FIRST.value
        computed = r1 * r1
        assert abs(FINE_STRUCTURE - computed) < 1e-10
        assert verify_fine_structure_invariant()


# =============================================================================
# Ordering Invariants (O1-O4)
# =============================================================================


class TestOrderingInvariants:
    """Tests for ordering invariants O1-O4."""

    def test_o1_rac_ordering(self) -> None:
        """O1: RAC₁ > RAC₂ > RAC₃ > RAC₄ > RAC₅ > RAC₆ > 0."""
        assert verify_rac_ordering()

    def test_o2_pi_ordering(self) -> None:
        """O2: π_red < π_green < π_blue."""
        assert RED_PI < GREEN_PI < BLUE_PI

    def test_o3_repitan_range(self) -> None:
        """O3: For all n: 0 < Repitan(n) ≤ 1."""
        assert verify_repitan_range_invariant()

    def test_o4_omega_indices(self) -> None:
        """O4: Omega format indices are 0-4."""
        assert verify_omega_indices()
        assert harmonic_from_omega(OmegaFormat.RED) == 0
        assert harmonic_from_omega(OmegaFormat.BLUE) == 4


# =============================================================================
# Conversion Invariants (C1-C3)
# =============================================================================


class TestConversionInvariants:
    """Tests for conversion invariants C1-C3."""

    def test_c1_omega_roundtrip(self) -> None:
        """C1: Omega roundtrip preserves value."""
        assert verify_all_omega_roundtrips(1.62)

    def test_c2_green_times_omega_equals_omega_minor(self) -> None:
        """C2: Green × Ω = Omega_Minor."""
        green = 1.62
        omega_minor = green_to_omega_minor(green)
        assert abs(omega_minor - green * OMEGA) < 1e-10

    def test_c3_green_div_omega_equals_omega_major(self) -> None:
        """C3: Green / Ω = Omega_Major."""
        green = 1.62
        omega_major = green_to_omega_major(green)
        assert abs(omega_major - green / OMEGA) < 1e-9


# =============================================================================
# Range Invariants (R1-R4)
# =============================================================================


class TestRangeInvariants:
    """Tests for range invariants R1-R4."""

    def test_r1_rac_range(self) -> None:
        """R1: 0 < RAC(i) < 1 for all i ∈ [1, 6]."""
        assert verify_rac_range()

    def test_r2_repitan_range(self) -> None:
        """R2: 0 < Repitan(n) ≤ 1 for all n ∈ [1, 27]."""
        for r in all_repitans():
            assert 0 < r.value <= 1

    def test_r3_coherence_bounds(self) -> None:
        """R3: Coherence bounds are [0, 1]."""
        assert verify_coherence_bounds()
        assert 0 <= COHERENCE_FLOOR < 1
        assert COHERENCE_CEILING == 1.0

    def test_r4_omega_range(self) -> None:
        """R4: Omega format index ∈ {0, 1, 2, 3, 4}."""
        assert verify_omega_range()


# =============================================================================
# Additional Property Tests
# =============================================================================


class TestRepitanProperties:
    """Additional tests for Repitan properties."""

    def test_smart_constructor_validates_range(self) -> None:
        """Smart constructor validates range."""
        for n in range(1, 28):
            assert Repitan.create(n) is not None
        assert Repitan.create(0) is None
        assert Repitan.create(28) is None
        assert Repitan.create(-1) is None

    def test_first_repitan_is_fine_structure_root(self) -> None:
        """First repitan is Fine Structure root."""
        assert abs(Repitan.FIRST.value - 1 / 27) < 1e-10

    def test_unity_repitan_equals_1(self) -> None:
        """Unity repitan equals 1."""
        assert Repitan.UNITY.value == 1

    def test_theta_repitan_roundtrip(self) -> None:
        """Theta/repitan roundtrip."""
        for r in all_repitans():
            theta = theta_from_repitan(r)
            r2 = repitan_from_theta(theta)
            assert r.index == r2.index


class TestRacProperties:
    """Additional tests for RAC properties."""

    def test_all_rac_values_in_range(self) -> None:
        """All RAC values are between 0 and 1."""
        for level in all_rac_levels():
            v = rac_value(level)
            assert 0 < v < 1


class TestGatesProperties:
    """Additional tests for Gates properties."""

    def test_full_coherence_grants_full_access(self) -> None:
        """Full coherence grants full access."""
        for level in all_rac_levels():
            result = access_level(1.0, level)
            assert result.is_full_access

    def test_zero_coherence_is_blocked(self) -> None:
        """Zero coherence is blocked."""
        for level in all_rac_levels():
            result = access_level(0.0, level)
            assert result.is_blocked

    def test_access_alpha_in_range(self) -> None:
        """Access alpha is in [0, 1]."""
        coherences = [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]
        for level in all_rac_levels():
            for c in coherences:
                result = access_level(c, level)
                assert 0 <= result.alpha <= 1

    def test_coherence_floor_is_phi_green_div_ankh(self) -> None:
        """Coherence floor is φ_green / Ankh."""
        assert verify_coherence_floor()


class TestSphericalProperties:
    """Additional tests for Spherical properties."""

    def test_radius_normalization_roundtrip(self) -> None:
        """Radius normalization roundtrip."""
        raw = ANKH / 2  # Half of Ankh
        normalized = normalize_radius(raw)
        denormalized = denormalize_radius(normalized)
        assert abs(denormalized - raw) < 1e-10

    def test_coordinate_validation(self) -> None:
        """Coordinate validation."""
        # Valid
        valid = RaCoordinate.create(
            Repitan.NINTH,
            RacLevel.RAC1,
            OmegaFormat.GREEN,
            0.5,
        )
        assert valid is not None

        # Invalid radius (negative)
        invalid_neg = RaCoordinate.create(
            Repitan.FIRST,
            RacLevel.RAC1,
            OmegaFormat.GREEN,
            -0.1,
        )
        assert invalid_neg is None

        # Invalid radius (> 1)
        invalid_high = RaCoordinate.create(
            Repitan.FIRST,
            RacLevel.RAC1,
            OmegaFormat.GREEN,
            1.1,
        )
        assert invalid_high is None
