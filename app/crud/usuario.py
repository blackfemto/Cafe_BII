from sqlalchemy.orm import Session
from app import models
import bcrypt
from datetime import datetime


def criar_usuario(db: Session, nome: str, email: str, senha: str, nivel: str = "GERENTE"):
    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    usuario = models.Usuario(
        nome=nome,
        email=email,
        senha_hash=senha_hash,
        nivel=nivel
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def buscar_usuario_por_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()


def autenticar_usuario(db: Session, email: str, senha: str):
    usuario = buscar_usuario_por_email(db, email)
    if not usuario:
        return None
    
    if not bcrypt.checkpw(senha.encode('utf-8'), usuario.senha_hash.encode('utf-8')):
        return None
    
    usuario.ultimo_login = datetime.now()
    db.commit()
    
    return usuario

def alterar_senha(db: Session, usuario_id: int, nova_senha: str):
    """Altera a senha de um usuário"""
    import bcrypt
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        return None
    
    senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    usuario.senha_hash = senha_hash
    db.commit()
    return usuario


def listar_usuarios(db: Session):
    """Lista todos os usuários"""
    return db.query(models.Usuario).order_by(models.Usuario.nome).all()


def desativar_usuario(db: Session, usuario_id: int):
    """Desativa um usuário"""
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if usuario:
        usuario.ativo = False
        db.commit()
        return True
    return False


def ativar_usuario(db: Session, usuario_id: int):
    """Ativa um usuário"""
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if usuario:
        usuario.ativo = True
        db.commit()
        return True
    return False
