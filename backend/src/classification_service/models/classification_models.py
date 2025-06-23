from src.classification_service.models.DualResNet import  dual_res_net
from src.shared.schemas import ClassificationRegime

models_dict = {
    ClassificationRegime.ResNet: dual_res_net
}