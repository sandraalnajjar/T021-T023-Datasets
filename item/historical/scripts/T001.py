import pint

from item.historical.scripts.util.managers.dataframe import ColumnName


# Dimensions and attributes which do not vary across this data set
COMMON = dict(
    # Rule: There is only one activity being perform in this dataset and that
    # is the "Freight Activity". We are setting, for each row, the variable
    # "Freight Activity"
    variable='Freight Activity',
    # Rule: Add the same source to all rows since all data comes from the same
    # source
    source='International Transport Forum',
    # Rule: Since all the data is associated to "Freight," the Service is
    # "Freight"
    service='Freight',
    # Rule: The dataset does not provide any data about those two columns, so
    # we added the default value of "All" in both cases
    technology='All',
    fuel='All',
    # Rule: Since all the data is about shipping, all rows have "Shipping" as
    # mode
    mode='Shipping',
    # Rule: Since all the data in this dataset is associted to coastal
    # shipping, the vehicle type is "Coastal"
    vehicle_type='Coastal',
)

# Columns to drop
DROP_COLUMNS = [
    'COUNTRY',
    'VARIABLE',
    'YEAR',
    'Flag Codes',
    'Flags',
    'PowerCode Code',
    'PowerCode',
    'Reference Period Code',
    'Reference Period',
    'Unit Code',
    'Unit',
]


def assign(df, dims):
    """Assign a single value for each dimension in *dims*."""
    # TODO move this method so it is usable across all scripts
    args = {}
    for dim in dims:
        # Standard name for the dimension
        name = getattr(ColumnName, dim.upper()).value
        # Common value for this data set
        args[name] = COMMON[dim]

    # Use the DataframeManager class
    # dataframeManager.simple_column_insert(df, name, value)

    # Use built-in pandas functionality, which is more efficient
    return df.assign(**args)

    # The Jupyter notebook echoes the data frame after each such step
    # print(df)


def convert_units(df, units_from, units_to):
    """Convert units of *df*."""
    # TODO move this method so it is usable across all scripts
    ureg = pint.get_application_registry()
    # Create a vector pint.Quantity; convert units
    qty = ureg.Quantity(df['Value'].values, units_from).to(units_to)
    # Assign Value and Unit columns in output DataFrame
    df['Value'] = qty.magnitude
    df['Unit'] = f'{qty.units:~}'


def check(df):
    """Check data set T001."""
    # Check that input data contain the expected variable name
    assert df['Variable'].unique() == ['Coastal shipping (national transport)']

    # Check that the input data contain the expected units
    assert df['PowerCode'].unique() == ['Millions']
    assert df['Unit'].unique() == ['Tonnes-kilometres']


def process(df):
    """Process data set T001."""
    # Getting a generic idea of what countries are missing values and dropping
    # NaN values
    #
    # Rule: Erase all value with NaN

    list_of_countries_with_missing_values = list(
        set(df[df['Value'].isnull()]["Country"]))
    print(">> Number of countries missing values: {}"
          .format(len(list_of_countries_with_missing_values)))
    print(">> Countries missing values:")
    print(list_of_countries_with_missing_values)
    print(">> Number of rows to erase: {}"
          .format(len(df[df['Value'].isnull()])))

    # Dropping the values
    df.dropna(inplace=True)

    # Assign single values for some dimensions
    df = assign(df, ['source', 'service', 'technology', 'fuel', 'mode',
                     'vehicle_type', 'variable'])

    # Convert to the preferred iTEM units
    # TODO read the preferred units (here 'Gt km / year') from a common place
    convert_units(df, 'Mt km / year', 'Gt km / year')

    return df
