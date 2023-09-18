#rotas do site
from flask import render_template, url_for, redirect
from flask_login import login_required, login_user, logout_user, current_user
from fakepinterest import app, database, bcrypt
from fakepinterest.forms import FormCriarConta, FormLogin, FormFoto
from fakepinterest.models import Usuario, Foto
import os
from werkzeug.utils import secure_filename

@app.route('/', methods=['GET', "POST"]) #rota para a homepage
def homepage(): #função que exibe a homepage
    form_login = FormLogin()
    if form_login.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=True)
            return redirect(url_for("perfildousuario", id_usuario=usuario.id))
    return render_template('homepage.html', form=form_login)

@app.route('/criarconta', methods=['GET', "POST"])
def criarconta():
    form_criarconta = FormCriarConta()
    if form_criarconta.validate_on_submit():
        senha_criptografada = bcrypt.generate_password_hash(form_criarconta.senha.data)
        usuario = Usuario(username=form_criarconta.username.data, 
                          senha=senha_criptografada, 
                          email=form_criarconta.email.data)
        database.session.add(usuario)
        database.session.commit()
        login_user(usuario, remember=True)
        return redirect(url_for("perfildousuario", id_usuario=usuario.id))
    return render_template("criarconta.html", form=form_criarconta)

@app.route('/perfil/<id_usuario>', methods=['GET', "POST"]) #rota para o perfil do usuário
@login_required #só permitir entrar nessa página quem estiver logado
def perfildousuario(id_usuario):
    if int(id_usuario) == int(current_user.id):
        form_foto = FormFoto()
        if form_foto.validate_on_submit():
            arquivo = form_foto.foto.data
            nome_seguro = secure_filename(arquivo.filename) #garantir que o nome do arquivo nao tenha caracteres zuados
            caminho_arquivo = os.path.join(os.path.abspath(os.path.dirname(__file__)), 
                                           app.config["UPLOAD_FOLDER"], 
                                           nome_seguro)#salvar o arquivo na pasta
            arquivo.save(caminho_arquivo)
            foto = Foto(imagem=nome_seguro, id_usuario=current_user.id) #registrar no banco de dados
            database.session.add(foto)
            database.session.commit()
        return render_template('perfil.html', usuario=current_user, form=form_foto)
    else:
        usuario = Usuario.query.get(int(id_usuario))
        return render_template('perfil.html', usuario=usuario, form=None)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))

@app.route('/feed')
@login_required
def feed():
    fotos = Foto.query.order_by(Foto.data_criacao.desc()).all()[:20] #selecionar todas as fotos no banco de dados em ordem de data de criação (max 20 fotos)
    return render_template("feed.html", fotos=fotos)