# tests/test_units_thermal.py
"""
Thermal unit regression tests — NIST SP811 Table 6 and conversion tables.
"""
import pytest
import quantia as qu


class TestThermalUnitsRegistered:

    def test_W_m2_registered(self):
        from quantia._registry import get_unit
        assert get_unit("W/m2").quantity == "heat_flux_density"

    def test_W_m_K_registered(self):
        from quantia._registry import get_unit
        assert get_unit("W/m_K").quantity == "thermal_conductivity"

    def test_J_K_registered(self):
        from quantia._registry import get_unit
        assert get_unit("J/K").quantity == "heat_capacity"

    def test_J_kg_K_registered(self):
        from quantia._registry import get_unit
        assert get_unit("J/kg_K").quantity == "specific_heat_capacity"

    def test_J_mol_registered(self):
        from quantia._registry import get_unit
        assert get_unit("J/mol").quantity == "molar_energy"

    def test_J_mol_K_registered(self):
        from quantia._registry import get_unit
        assert get_unit("J/mol_K").quantity == "molar_heat_capacity"


class TestImperialThermal:

    def test_BTU_IT_h_to_W(self):
        # NIST: 1 BTU_IT/h = 2.930 711 E-01 W
        assert qu.Q(1.0, "BTU_IT/h").to("W").value == pytest.approx(
               2.930_711e-1, rel=1e-6)

    def test_BTU_IT_lb_to_J_kg(self):
        # NIST: 1 BTU_IT/lb = 2.326 E+03 J/kg (exact)
        # BTU_IT/lb is specific energy (J/kg), not specific heat (J/(kg·K))
        assert qu.Q(1.0, "BTU_IT/lb").to("J/kg").value == pytest.approx(
            2.326e3, rel=1e-6)

    def test_BTU_IT_lb_F_to_J_kg_K(self):
        # NIST: 1 BTU_IT/(lb·°F) = 4.1868 E+03 J/(kg·K)
        assert qu.Q(1.0, "BTU_IT/lb_F").to("J/kg_K").value == pytest.approx(
               4.1868e3, rel=1e-6)