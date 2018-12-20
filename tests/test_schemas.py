from Jumpscale import j


class TestGedisSchema:

    def test_schemas_loading(self):
        from zerorobot import gedis
        for schema in gedis.SCHEMAS:
            url = _extract_url(schema)
            assert j.data.schema.exists(url)
            _ = j.data.schema.get(url=url)


def _extract_url(schema_txt):
    line = schema_txt.strip().splitlines()[0]
    return line.split('=', 1)[1].strip()
