from generated.apps import Commonv1Value


def patch_common_value():
    origin_from_dict = Commonv1Value.from_dict
    origin_to_dict = Commonv1Value.to_dict

    def new_from_dict(obj: dict):
        temp_obj = obj
        if isinstance(obj, str) or isinstance(obj, int) or isinstance(obj, float):
            temp_obj = {
                'value': str(obj),
            }
        return origin_from_dict(temp_obj)

    def new_to_dict(self):
        if hasattr(self, 'value') and self.value:
            return str(self.value)
        return origin_to_dict(self)

    Commonv1Value.from_dict = new_from_dict
    # Commonv1Value.to_dict = new_to_dict


