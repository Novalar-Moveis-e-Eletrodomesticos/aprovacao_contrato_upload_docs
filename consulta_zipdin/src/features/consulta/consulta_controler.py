from src.services.consulta.consulta_service import ConsultaService

class ConsultaController:
    def fetchConsulta(usuarioid,filialid):
        data = ConsultaService.fetch_consulta(v_idusuario=usuarioid,v_idfilial=filialid)
        return data
    
    def fecharPedido(v_contrato,v_status,v_obs):
        data = ConsultaService.baixar_venda(contrato=v_contrato,status=v_status,obs=v_obs)
        return data
    
    def fetchZipdin(contratoexterno):
        dados = ConsultaService.zipdin(contrato=contratoexterno)
        return dados