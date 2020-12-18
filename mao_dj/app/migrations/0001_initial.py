# Generated by Django 3.1.4 on 2020-12-18 15:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Audience',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Award',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hasNickname', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='CollectiveAgent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='ContentRating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hasDescription', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Occupation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Situation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isSettingFor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.award')),
            ],
        ),
        migrations.CreateModel(
            name='ActingSituation',
            fields=[
                ('situation_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='app.situation')),
            ],
            bases=('app.situation',),
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('place_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='app.place')),
                ('label', models.CharField(max_length=255)),
            ],
            bases=('app.place',),
        ),
        migrations.CreateModel(
            name='FilmCast',
            fields=[
                ('collectiveagent_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='app.collectiveagent')),
                ('isParticipantIn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.actingsituation')),
            ],
            bases=('app.collectiveagent',),
        ),
        migrations.CreateModel(
            name='FilmCrew',
            fields=[
                ('collectiveagent_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='app.collectiveagent')),
            ],
            bases=('app.collectiveagent',),
        ),
        migrations.CreateModel(
            name='FilmMakingSituation',
            fields=[
                ('situation_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='app.situation')),
                ('hasCast', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.filmcast')),
            ],
            bases=('app.situation',),
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hasGender', models.CharField(choices=[('female', 'Female'), ('male', 'Male'), ('non-binary', 'Non Binary')], max_length=255)),
                ('hasName', models.CharField(max_length=255)),
                ('eligibleFor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.award')),
                ('hasOccupation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.occupation')),
                ('actsIn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.filmmakingsituation')),
            ],
        ),
        migrations.AddField(
            model_name='occupation',
            name='isOccupationof',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.person'),
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hasSubGenre', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='isSubGenreOf', to='app.genre')),
            ],
        ),
        migrations.CreateModel(
            name='Film',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dateReleased', models.CharField(max_length=255)),
                ('hasFeatureLengthInMinutes', models.IntegerField()),
                ('hasInitialReleaseYear', models.IntegerField()),
                ('hasTitle', models.CharField(max_length=255)),
                ('hasWikipediaLink', models.CharField(max_length=255)),
                ('isBritishFilm', models.BooleanField()),
                ('isAdult', models.BooleanField()),
                ('avg_rating', models.CharField(max_length=255)),
                ('eligibleFor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.award')),
                ('hasAudience', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.audience')),
                ('hasContentRating', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.contentrating')),
                ('hasFilmingLocation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='filming_location_of_films', to='app.place')),
                ('hasGenre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.genre')),
                ('hasLanguage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='language_of_films', to='app.language')),
                ('hasOriginalLanguage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='original_language_of_films', to='app.language')),
                ('hasPrequels', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='hasSequels', to='app.film')),
                ('hasSubTitleInLanguage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subtitle_of_films', to='app.language')),
                ('hasCountryOfOrigin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='origin_country_of_films', to='app.country')),
            ],
        ),
        migrations.AddField(
            model_name='collectiveagent',
            name='hasMember',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.person'),
        ),
        migrations.CreateModel(
            name='Character',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hasGender', models.CharField(choices=[('female', 'Female'), ('male', 'Male'), ('non-binary', 'Non Binary')], max_length=255)),
                ('hasImportance', models.CharField(choices=[('main', 'Main'), ('side', 'Side'), ('extra', 'Extra')], max_length=255)),
                ('hasCharacterTitle', models.CharField(max_length=255)),
                ('hasName', models.CharField(max_length=255)),
                ('actedBy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.person')),
            ],
        ),
        migrations.CreateModel(
            name='AwardCeremony',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dateHeld', models.CharField(max_length=255)),
                ('hasEditionNumber', models.IntegerField()),
                ('yearScreened', models.IntegerField()),
                ('follow', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='followedBy', to='app.awardceremony')),
                ('hasAward', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.award')),
            ],
        ),
        migrations.CreateModel(
            name='AwardCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('forOccupation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.occupation')),
            ],
        ),
        migrations.AddField(
            model_name='award',
            name='hasAwardCategory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.awardcategory'),
        ),
        migrations.AddField(
            model_name='award',
            name='hasPart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.awardceremony'),
        ),
        migrations.AddField(
            model_name='award',
            name='presentedBy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.organization'),
        ),
        migrations.CreateModel(
            name='NominationSituation',
            fields=[
                ('situation_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='app.situation')),
                ('win', models.BooleanField()),
                ('forFilm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.film')),
                ('hasAward', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.award')),
                ('hasAwardCategory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.awardcategory')),
                ('hasAwardCeremony', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.awardceremony')),
                ('isGivenTo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.person')),
            ],
            bases=('app.situation',),
        ),
        migrations.CreateModel(
            name='MovieStudio',
            fields=[
                ('organization_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='app.organization')),
                ('locatedIn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.place')),
            ],
            bases=('app.organization',),
        ),
        migrations.AddField(
            model_name='filmmakingsituation',
            name='hasCinematographer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cinematographer_of_film_making_situation_set', to='app.person'),
        ),
        migrations.AddField(
            model_name='filmmakingsituation',
            name='hasComposer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='composer_of_film_making_situation_set', to='app.person'),
        ),
        migrations.AddField(
            model_name='filmmakingsituation',
            name='hasCrew',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.filmcrew'),
        ),
        migrations.AddField(
            model_name='filmmakingsituation',
            name='hasDirector',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='director_of_film_making_situation_set', to='app.person'),
        ),
        migrations.AddField(
            model_name='filmmakingsituation',
            name='hasFilm',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.film'),
        ),
        migrations.AddField(
            model_name='filmmakingsituation',
            name='hasPart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.actingsituation'),
        ),
        migrations.AddField(
            model_name='filmmakingsituation',
            name='hasProducer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='producer_of_film_making_situation_set', to='app.person'),
        ),
        migrations.AddField(
            model_name='filmcrew',
            name='isParticipantIn',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.filmmakingsituation'),
        ),
        migrations.AddField(
            model_name='award',
            name='hasSetting',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.nominationsituation'),
        ),
        migrations.AddField(
            model_name='actingsituation',
            name='hasActor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.person'),
        ),
        migrations.AddField(
            model_name='actingsituation',
            name='hasCharacter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.character'),
        ),
        migrations.AddField(
            model_name='actingsituation',
            name='hasFilm',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.film'),
        ),
        migrations.AddField(
            model_name='actingsituation',
            name='isPartOf',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.filmmakingsituation'),
        ),
    ]