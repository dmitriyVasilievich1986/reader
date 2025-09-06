from marshmallow import EXCLUDE, fields, Schema


class BookPageSchema(Schema):
    id = fields.Integer(required=True)
    position = fields.Integer(required=True)
    cover = fields.String(required=True)

    class Meta:
        unknown = EXCLUDE
