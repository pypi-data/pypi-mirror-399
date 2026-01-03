from datetime import date

from snowflake.snowpark.functions import col
from snowflake.snowpark import DataFrame

from ..config import MSP_PROD_MAX, TABLE_CONFIGS
from ....utils.decorators import time_function
from ....utils.etl import ETL
from ....utils.logger import Logger

MODULE_NAME: Final[str] = "processors/msp_processor.py"

class MSPProcessor:
    """
    Processor for dealing with transformations related to the medicare secondary payer table extracts
    """
    def __init__(self):
        self.processing_year = processing_year
        self.logger = Logger()
        self.msp_prod_max = MSP_PROD_MAX
        self.etl = ETL()
        self.msp_table_config = TABLE_CONFIGS["MSP"].generate_table_name()

    @time_function(f"{MODULE_NAME}.run")
    def process(self,) -> DataFrame:
        if self.processing_year > self.msp_prod_max:
            self.logger.info(
                message=f"Year {self.processing_year} > {self.msp_prod_max}: Processing from Snowflake",
                context=MODULE_NAME
            )
            return self._extract_msp_data()
        else:
            self.logger.info(
                message=f"Year {self.processing_year} <= {self.msp_prod_max}: Using historical data",
                context=MODULE_NAME
            )
            reutrn self._process_from_historical()

    def _extract_msp_data(self) -> DataFrame:
        # Snowpark transformations...
        ...

    def _process_from_historical(self) -> DataFrame:
        # Snowpark transformations...
        ...

"""
Maybe there are other private methods that support these ones? 

At the end, process() is the orchestrator for the processor level. 
process() will always return a dataframe to be returns to the pipeline orchestrator. in that case, BeneficiaryPipeline.

Processors manage their own extracts using config.py to get their table data.
config.py is already generated.

Whenever we create a new processor, we want to create a unit test file under pipelines/{pipeline}/processors/tests
For reference, the new processor will be places in pipelines/{pipeline}/processors/{processor_name}_processor.py

Another feature of processors is that they are automatically imported to their respective runner file upon creation.

"""