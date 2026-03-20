# The Unit System

quantia uses a string-based unit expression parser that understands
standard mathematical notation.

## Writing unit expressions
```python
import quantia as qu

qu.Q(9.81,  'm/s^2')          # acceleration
qu.Q(1.0,   'kg·m/s^2')       # newton (· or * for multiplication)
qu.Q(4.0,   'm^(1/2)')        # rational exponents
qu.Q(1.0,   'kg/m^2/s')       # chained division
qu.Q(100.0, 'psia')           # registered atomic symbol
qu.Q(1.0,   'm3')             # atomic alias for m^3
```

## Unit compatibility

Two units are compatible when they reduce to the same SI base
dimensions. quantia checks this automatically:
```python
# Compatible — both reduce to m·s⁻¹
qu.Q(60.0, 'mph').to('m/s')

# Incompatible — pressure vs length
qu.Q(1.0, 'Pa') + qu.Q(1.0, 'm')   # → IncompatibleUnitsError
```

## Compound units

Arithmetic between `UnitFloat` instances builds compound units:
```python
force  = qu.Q(10.0, 'N')
area   = qu.Q(2.0,  'm^2')
stress = force / area           # UnitFloat(5.0, 'Pa')
                                # N/m² → Pa via alias
```

## Registering custom units
```python
from quantia import register
from quantia._registry import Unit

register('furlong', Unit('furlong', 'length', 'm', 201.168, 'furlong'))
qu.Q(8.0, 'furlong').to('km')   # UnitFloat(1.609..., 'km')
```

## Registering custom tagged units
```python
from quantia import register_tagged

register_tagged('Sm3_inj', 'm3', 'injection')   # injection water volumes
register_tagged('Sm3_prod', 'm3', 'produced')   # produced water volumes

inj  = qu.Q(1000.0, 'Sm3_inj')
prod = qu.Q(800.0,  'Sm3_prod')
net  = inj - prod   # → IncompatibleUnitsError — injection ≠ produced
```