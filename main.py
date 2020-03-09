from flask import Flask, render_template, jsonify, request, redirect
import cx_Oracle
from datetime import datetime

app = Flask(__name__)
with open(app.root_path + '\config.cfg', 'r') as f:
    app.config['ORACLE_URI'] = f.readline()

con = cx_Oracle.connect("student", "student", "localhost/xe")


@app.route('/')
@app.route('/caine')
def caine_fct():
    caini = []
    cur = con.cursor()
    cur.execute('select * from caine c where c.id not in (select id from adoptie ) order by c.id')
    for result in cur:
        caine = {}
        caine['id'] = result[0]
        caine['nume'] = result[1]
        caine['sex'] = result[2]
        caine['talie'] = result[3]
        caine['data_primirii'] = datetime.strptime(str(result[4]), '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%y')
        caine['observatii'] = result[5]
        caine['nr_cazare'] = result[6]

        caini.append(caine)

    cur.execute('select * from caine order by id')
    istoric=[]
    for result in cur:
        c = {}
        c['id'] = result[0]
        c['nume'] = result[1]
        c['sex'] = result[2]
        c['talie'] = result[3]
        c['data_primirii'] = datetime.strptime(str(result[4]), '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%y')
        c['observatii'] = result[5]
        c['nr_cazare'] = result[6]

        istoric.append(c)
    cazare = []
  
    cur.execute('select distinct cz.nr_cazare, talie from caine c, cazare cz , '
                '(select count(id) cati, nr_cazare from caine group by nr_cazare) x '
                'where c.nr_cazare=cz.nr_cazare '
                'and x.nr_cazare=cz.nr_cazare and '
                "((talie='mica' and cati<4 ) or (talie='medie' and cati<3) or (talie='mare' and cati<2)) "
                'and cati<cz.spatiu_cazare')

    for result in cur:
        cazare.append([result[0], result[1]])
    cur.execute('select nr_cazare from cazare cz where cz.nr_cazare not in (select  nr_cazare from caine )')
    for result in cur:
        cazare.append([result[0],'libera'])
    cur.close()
    return render_template('caine.html', caine=caini, cazare=cazare,istoric=istoric)


@app.route('/add_caine', methods=['POST'])
def add_caine_fct():
    if request.method == 'POST':
        cur = con.cursor()
        values = []
        values.append("'" + request.form['nume'] + "'")
        values.append("'" + request.form['sex'] + "'")
        values.append("'" + request.form['talie'] + "'")
        values.append(
            "'" + datetime.strptime(str(request.form['data_primirii']), '%d-%m-%Y').strftime('%d-%m-%Y') + "'")
        values.append("'" + request.form['observatii'] + "'")
        values.append("'" + request.form['nr_cazare'] + "'")
        query = 'insert into caine values(NULL,' + ', '.join(values) + ')'

        cur.execute(query)

        cur.execute('commit')
        cur.close()
        return redirect('/caine')


@app.route('/get_caine', methods=['POST'])
def get_caine_fct():
    id=request.form['id']
    cur=con.cursor()
    cur.execute('select * from caine where id=' + id)
    c = cur.fetchone()
    nume = c[1]
    sex = c[2]
    talie = c[3]
    data=datetime.strptime(str(c[4]), '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
    obs=c[5]
    nr=c[6]
    cazare=[]
    if talie == "mica":
        dim_max=4
    else:
        if talie == "medie":
            dim_max=3
        else:
            dim_max=2

    cur.execute('select distinct cz.nr_cazare, talie from caine c, cazare cz , '
                '(select count(id) cati, nr_cazare from caine group by nr_cazare) x '
                'where c.nr_cazare=cz.nr_cazare '
                'and x.nr_cazare=cz.nr_cazare and '
                "talie='%s' and cati<%s "
                'and cati<cz.spatiu_cazare and cz.nr_cazare!=%s' %(talie,dim_max,nr))

    for result in cur:
        cazare.append(result[0])
    cur.execute('select nr_cazare from cazare cz where cz.nr_cazare not in (select  nr_cazare from caine )')
    for result in cur:
        cazare.append(result[0])
    cur.close()
    return render_template('/edit_caine.html',id=id,nume=nume, sex=sex,talie=talie,data=data,obs=obs,nr=nr,cazare=cazare)


@app.route('/edit_caine', methods=['POST'])
def edit_caine_fct():
    id = "'" + request.form['id'] + "'"
    nume = "'"+request.form['nume']+"'"
    obs = "'"+request.form['observatii']+"'"
    nr = "'"+request.form['nr_cazare']+"'"

    cur = con.cursor()
    query = "update caine set nume=%s, nr_cazare=%s, observatii=%s where id=%s" % (nume, nr, obs, id)
    cur.execute(query)


    cur.close()
    return redirect('/caine')


@app.route('/del_caine', methods=['POST'])
def del_caine_fct():
    cur = con.cursor()
    cur.execute('delete from caine where id=' + request.form['id'])
    cur.execute('commit')
    cur.close()
    return redirect('/caine')


@app.route('/cazare')
def cazare_fct():
    cazari = []

    cur = con.cursor()
    cur.execute('select * from cazare order by nr_cazare')
    for result in cur:
        cazare = {}
        cazare['nr_cazare'] = result[0]
        cazare['tip_cazare'] = result[1]
        cazare['spatiu_cazare'] = result[2]

        cazari.append(cazare)
    cur.close()

    return render_template('cazare.html', cazare=cazari)


@app.route('/add_cazare', methods=['POST'])
def add_cazare_fct():
    if request.method == 'POST':
        cur = con.cursor()
        values = []
        values.append("'" + request.form['nr_cazare'] + "'")
        values.append("'" + request.form['tip_cazare'] + "'")
        values.append("'" + request.form['spatiu_cazare'] + "'")
        query = 'insert into cazare values(' + ', '.join(values) + ')'

        cur.execute(query)
        cur.execute('commit')
        cur.close()
        return redirect('/cazare')


@app.route('/persoana')
def persoana_fct():
    persoane = []

    cur = con.cursor()
    cur.execute('select * from persoana order by id_pers')
    for result in cur:
        persoana = {}
        persoana['id_pers'] = result[0]
        persoana['nume_pers'] = result[1]
        persoana['adr_pers'] = result[2]
        persoana['telefon_pers'] = result[3]
        persoana['observatii_pers'] = result[4]

        persoane.append(persoana)
    cur.close()
    return render_template('persoana.html', persoana=persoane)


@app.route('/add_persoana', methods=['POST'])
def add_persoana_fct():
    if request.method == 'POST':
        cur = con.cursor()
        values = []
        values.append("'" + request.form['nume_pers'] + "'")
        values.append("'" + request.form['adr_pers'] + "'")
        values.append("'" + request.form['telefon_pers'] + "'")
        values.append("'" + request.form['observatii_pers'] + "'")
        query = 'insert into persoana values(NULL,' + ', '.join(values) + ')'

        cur.execute(query)
        cur.execute('commit')
        cur.close()
        return redirect('/persoana')


@app.route('/get_persoana', methods=['POST'])
def get_persoana_fct():
    id=request.form['id_pers']
    cur=con.cursor()
    cur.execute('select * from persoana where id_pers=' + id)
    pers = cur.fetchone()
    nume = pers[1]
    adr = pers[2]
    tel = pers[3]
    obs=pers[4]

    return render_template('/edit_persoana.html',id=id,nume=nume, adr=adr,tel=tel,obs=obs)


@app.route('/edit_persoana', methods=['POST'])
def edit_persoana_fct():

    nume="'"+request.form['nume_pers']+"'"
    adr="'"+request.form['adr_pers']+"'"
    tel="'"+request.form['telefon_pers']+"'"
    obs="'"+request.form['observatii_pers']+"'"

    cur = con.cursor()
    id = "'"+request.form['id_pers']+"'"
    query="update persoana set nume_pers=%s, adr_pers=%s, telefon_pers=%s, observatii_pers=%s where id_pers=%s" %(nume, adr, tel, obs, id)
    cur.execute(query)
    cur.close()
    return redirect('/persoana')


@app.route('/adoptie')
def adoptie_fct():
    adoptii = []

    cur = con.cursor()
    cur1 = con.cursor()
    cur.execute('select * from adoptie order by nr_adoptie')
    for result in cur:
        adoptie = {}
        adoptie['nr_adoptie'] = result[0]
        adoptie['tip_adoptie'] = result[1]
        adoptie['data_adoptie'] = datetime.strptime(str(result[2]), '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%y')
        adoptie['id'] = result[3]
        adoptie['id_pers'] = result[4]
        cur1.execute('select nume_pers from persoana where id_pers='+ str(adoptie['id_pers']))
        adoptie['nume_pers'] = cur1.fetchone()[0]
        adoptii.append(adoptie)
    cur.close()
    persoane = []
    cur1.execute('select id_pers,nume_pers from persoana')
    for result in cur1:
        persoane.append([result[0], result[1]])
    caini=[]
    cur1.execute('select c.id from caine c where c.id not in (select id from adoptie )')
    for result in cur1:
        caini.append(result[0])
    return render_template('adoptie.html', adoptie=adoptii,persoana=persoane,caine=caini)


@app.route('/add_adoptie', methods=['POST'])
def add_adoptie_fct():
    if request.method == 'POST':
        cur = con.cursor()
        values = []
        values.append("'" + request.form['tip_adoptie'] + "'")
        values.append(
            "'" + datetime.strptime(str(request.form['data_adoptie']), '%d-%m-%Y').strftime('%d-%m-%Y') + "'")
        id = "'" + request.form['id'] + "'"
        values.append(id)
        values.append("'" + request.form['id_pers'] + "'")
        query = 'insert into adoptie values(NULL,' + ', '.join(values) + ')'
        cur.execute(query)


        cur.execute('commit')
        cur.close()
        return redirect('/adoptie')


@app.route('/donatie')
def donatie_fct():
    donatii = []

    cur = con.cursor()
    cur1 = con.cursor()
    cur.execute('select * from donatie order by nr_donatie')
    for result in cur:
        donatie = {}
        donatie['nr_donatie'] = result[0]
        donatie['tip_donatie'] = result[1]
        donatie['data_donatie'] = datetime.strptime(str(result[2]), '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%y')
        donatie['id_pers'] = result[3]
        cur1.execute('select nume_pers from persoana where id_pers=' + str(donatie['id_pers']))
        donatie['nume_pers'] = cur1.fetchone()[0]
        donatii.append(donatie)
    cur.close()

    persoane=[]
    cur1.execute('select id_pers,nume_pers from persoana')
    for result in cur1:
        persoane.append([result[0],result[1]])
    return render_template('donatie.html', donatie=donatii, persoana=persoane)


@app.route('/add_donatie', methods=['POST'])
def add_donatie_fct():
    if request.method == 'POST':
        cur = con.cursor()
        values = []
        values.append("'" + request.form['tip_donatie'] + "'")
        values.append(
            "'" + datetime.strptime(str(request.form['data_donatie']), '%d-%m-%Y').strftime('%d-%m-%Y') + "'")
        values.append("'" + request.form['id_pers'] + "'")
        query = 'insert into donatie values(NULL,' + ', '.join(values) + ')'

        cur.execute(query)
        cur.execute('commit')
        cur.close()
        return redirect('/donatie')


@app.route('/fisa_medicala')
def fisa_fct():
    fise = []
    cur = con.cursor()
    cur.execute('select * from fisa_medicala order by id_fisa')
    for result in cur:
        fisa = {}
        fisa['id_fisa'] = result[0]
        fisa['tip_procedura'] = result[1]
        fisa['cost_procedura'] = result[2]
        fisa['data_procedura'] = datetime.strptime(str(result[3]), '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%y')
        fisa['id'] = result[4]
        fisa['nume_medic'] = result[5]
        fisa['id_medic'] = result[6]
        fise.append(fisa)
    cur.close()
    caini = []
    cur = con.cursor()
    cur.execute('select c.id from caine c where c.id not in (select id from adoptie )')
    for result in cur:
        caini.append(result[0])
    cur.close()
    medici = []
    cur = con.cursor()
    cur.execute('select id_medic, nume_medic from medic_veterinar')
    for result in cur:
        medici.append([result[0], result[1]])
    cur.close()
    return render_template('fisa_medicala.html', fisa=fise, caine=caini, medic_veterinar=medici)


@app.route('/get_fisa', methods=['POST'])
def get_fisa_fct():
    id_f=request.form['id_caine']

    return render_template('/edit_persoana.html',id_f=id_f)


@app.route('/add_fisa', methods=['POST'])
def add_fisa_fct():
    if request.method == 'POST':
        cur = con.cursor()
        values = []

        values.append("'" + request.form['tip_procedura'] + "'")
        values.append("'" + request.form['cost_procedura'] + "'")
        values.append(
            "'" + datetime.strptime(str(request.form['data_procedura']), '%d-%m-%Y').strftime('%d-%m-%Y') + "'")
        values.append("'" + request.form['id'] + "'")
        id_m = "'" + request.form['id_medic'] + "'"

        cur1 = con.cursor()
        cur1.execute('select nume_medic from medic_veterinar where id_medic=' + id_m)
        nume= cur1.fetchone()
        cur1.close()

        values.append("'" + nume[0] + "'")
        values.append(id_m)
        query = 'insert into fisa_medicala values(NULL,' + ', '.join(values) + ')'
        cur.execute(query)
        cur.execute('commit')
        cur.close()
        return redirect('/fisa_medicala')


@app.route('/medic_veterinar')
def medic_fct():
    medici = []
    cur = con.cursor()
    cur.execute('select * from medic_veterinar order by id_medic')
    for result in cur:
        medic = {}
        medic['id_medic'] = result[0]
        medic['nume_medic'] = result[1]
        medic['telefon_medic'] = result[2]
        medici.append(medic)
    cur.close()

    return render_template('medic_veterinar.html', medic=medici)


@app.route('/add_medic', methods=['POST'])
def add_medic_fct():
    if request.method == 'POST':
        cur = con.cursor()
        values = []
        values.append("'" + request.form['id_medic'] + "'")
        values.append("'" + request.form['nume_medic'] + "'")
        values.append("'" + request.form['telefon_medic'] + "'")
        query = 'insert into medic_veterinar values(' + ', '.join(values) + ')'

        cur.execute(query)
        cur.execute('commit')
        cur.close()
        return redirect('/medic_veterinar')


@app.route('/get_medic', methods=['POST'])
def get_medic_fct():
    id=request.form['id_medic']
    cur=con.cursor()
    cur.execute('select * from medic_veterinar where id_medic=' + id)
    medic = cur.fetchone()
    nume = medic[1]
    tel = medic[2]
    return render_template('/edit_medic.html',id=id,nume=nume, tel=tel)


@app.route('/edit_medic', methods=['POST'])
def edit_medic_fct():
    id = "'" + request.form['id_medic'] + "'"
    tel="'"+request.form['telefon_medic']+"'"
    cur = con.cursor()
    query='update medic_veterinar set telefon_medic='+ tel+ ' where id_medic=' + id
    cur.execute(query)
    cur.close()
    return redirect('/medic_veterinar')


@app.route('/del_medic', methods=['POST'])
def del_medic_fct():
    cur = con.cursor()
    cur.execute('delete from medic_veterinar where id_medic=' + request.form['id_medic'])
    cur.execute('commit')
    cur.close()
    return redirect('/medic_veterinar')


if __name__ == '__main__':
    app.run(debug=True)
    con.close()
