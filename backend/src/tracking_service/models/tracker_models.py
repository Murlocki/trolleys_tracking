from src.shared.schemas import TrackingRegime
from src.tracking_service.models.DeepsortModel import DeepsortModel, parameters

models_dict = {
    TrackingRegime.deepsort: DeepsortModel
}
models_params_dict = {
    TrackingRegime.deepsort: parameters
}