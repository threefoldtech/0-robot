from Jumpscale import j

from .schemas import SCHEMAS

logger = j.logger.get(__name__)

# Load all schemas
for schema in SCHEMAS:
    logger.info("loading schema %s", schema.strip().splitlines()[0])
    j.data.schema.get(schema_text_path=schema)
