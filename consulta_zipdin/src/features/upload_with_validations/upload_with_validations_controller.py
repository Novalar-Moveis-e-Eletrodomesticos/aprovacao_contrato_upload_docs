from common.generic.log import setup_logging
from src.services.upload_with_validation.upload_with_validation_service import UploadWithValidationService
log = setup_logging()
class UploadWithValidationsController:
    def fetchConsulta(usuarioid,filialid):
        data = UploadWithValidationService.fetch_consulta(v_idusuario=usuarioid,v_idfilial=filialid)
        return data
    
    def fecharPedido(v_contrato,v_status,v_obs):
        log.info('entrou em def fechar pedido')
        data = UploadWithValidationService.baixar_venda(contrato=v_contrato,status=v_status,obs=v_obs)
        return data
    
