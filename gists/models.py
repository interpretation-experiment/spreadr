from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
import networkx as nx

from solo.models import SingletonModel


DEFAULT_LANGUAGE = 'english'
OTHER_LANGUAGE = 'other'
LANGUAGE_CHOICES = sorted(
    [('french', 'French'),
     ('english', 'English'),
     ('spanish', 'Spanish'),
     ('italian', 'Italian'),
     ('german', 'German'),
     ('other', 'Other')],
    key=lambda l: l[1])
BUCKET_CHOICES = sorted(
    [('training', 'Training'),
     ('experiment', 'Experiment'),
     ('game', 'Game')],
    key=lambda b: b[1])
GENDER_CHOICES = [('female', 'Female'),
                  ('male', 'Male'),
                  ('other', 'Other')]
ISCO_MAJOR_CHOICES = [
    ('-', 'None'),
    ('1', 'Managers'),
    ('2', 'Professionals'),
    ('3', 'Technicians and associate professionals'),
    ('4', 'Clerical support workers'),
    ('5', 'Service and sales workers'),
    ('6', 'Skilled agricultural, forestry and fishery workers'),
    ('7', 'Craft and related trades workers'),
    ('8', 'Plant and machine operators, and assemblers'),
    ('9', 'Elementary occupations'),
    ('0', 'Armed forces occupations'),
]
ISCO_SUBMAJOR_CHOICES = [
    ('--', 'None'),
    ('11', 'Chief executives, senior officials and legislators'),
    ('12', 'Administrative and commercial managers'),
    ('13', 'Production and specialized services managers'),
    ('14', 'Hospitality, retail and other services managers'),
    ('21', 'Science and engineering professionals'),
    ('22', 'Health professionals'),
    ('23', 'Teaching professionals'),
    ('24', 'Business and administration professionals'),
    ('25', 'Information and communications technology professionals'),
    ('26', 'Legal, social and cultural professionals'),
    ('31', 'Science and engineering associate professionals'),
    ('32', 'Health associate professionals'),
    ('33', 'Business and administration associate professionals'),
    ('34', 'Legal, social, cultural and related associate professionals'),
    ('35', 'Information and communications technicians'),
    ('41', 'General and keyboard clerks'),
    ('42', 'Customer services clerks'),
    ('43', 'Numerical and material recording clerks'),
    ('44', 'Other clerical support workers'),
    ('51', 'Personal service workers'),
    ('52', 'Sales workers'),
    ('53', 'Personal care workers'),
    ('54', 'Protective services workers'),
    ('61', 'Market-oriented skilled agricultural workers'),
    ('62', 'Market-oriented skilled forestry, fishery and hunting workers'),
    ('63', 'Subsistence farmers, fishers, hunters and gatherers'),
    ('71', 'Building and related trades workers, excluding electricians'),
    ('72', 'Metal, machinery and related trades workers'),
    ('73', 'Handicraft and printing workers'),
    ('74', 'Electrical and electronic trades workers'),
    ('75', 'Food processing, wood working, garment and other '
           'craft and related trades workers'),
    ('81', 'Stationary plant and machine operators'),
    ('82', 'Assemblers'),
    ('83', 'Drivers and mobile plant operators'),
    ('91', 'Cleaners and helpers'),
    ('92', 'Agricultural, forestry and fishery labourers'),
    ('93', 'Labourers in mining, construction, manufacturing and transport'),
    ('94', 'Food preparation assistants'),
    ('95', 'Street and related sales and service workers'),
    ('96', 'Refuse workers and other elementary workers'),
    ('01', 'Commissioned armed forces officers'),
    ('02', 'Non-commissioned armed forces officers'),
    ('03', 'Armed forces occupations, other ranks'),
]
ISCO_MINOR_CHOICES = [
    ('---', 'None'),
    ('111', 'Legislators and senior officials'),
    ('112', 'Managing directors and chief executives'),
    ('121', 'Business services and administration managers'),
    ('122', 'Sales, marketing and development managers'),
    ('131', 'Production managers in agriculture, forestry and fisheries'),
    ('132', 'Manufacturing, mining, construction, and distribution managers'),
    ('133', 'Information and communications technology service managers'),
    ('134', 'Professional services managers'),
    ('141', 'Hotel and restaurant managers'),
    ('142', 'Retail and wholesale trade managers'),
    ('143', 'Other services managers'),
    ('211', 'Physical and earth science professionals'),
    ('212', 'Mathematicians, actuaries and statisticians'),
    ('213', 'Life science professionals'),
    ('214', 'Engineering professionals (excluding electrotechnology)'),
    ('215', 'Electrotechnology engineers'),
    ('216', 'Architects, planners, surveyors and designers'),
    ('221', 'Medical doctors'),
    ('222', 'Nursing and midwifery professionals'),
    ('223', 'Traditional and complementary medicine professionals'),
    ('224', 'Paramedical practitioners'),
    ('225', 'Veterinarians'),
    ('226', 'Other health professionals'),
    ('227', 'Medical Assistant professionals'),
    ('231', 'University and higher education teachers'),
    ('232', 'Vocational education teachers'),
    ('233', 'Secondary education teachers'),
    ('234', 'Primary school and early childhood teachers'),
    ('235', 'Other teaching professionals'),
    ('241', 'Finance professionals'),
    ('242', 'Administration professionals'),
    ('243', 'Sales, marketing and public relations professionals'),
    ('251', 'Software and applications developers and analysts'),
    ('252', 'Database and network professionals'),
    ('261', 'Legal professionals'),
    ('262', 'Librarians, archivists and curators'),
    ('263', 'Social and religious professionals'),
    ('264', 'Authors, journalists and linguists'),
    ('265', 'Creative and performing artists'),
    ('311', 'Physical and engineering science technicians'),
    ('312', 'Mining, manufacturing and construction supervisors'),
    ('313', 'Process control technicians'),
    ('314', 'Life science technicians and related associate professionals'),
    ('315', 'Ship and aircraft controllers and technicians'),
    ('321', 'Medical and pharmaceutical technicians'),
    ('322', 'Nursing and midwifery associate professionals'),
    ('323', 'Traditional and complementary medicine associate professionals'),
    ('324', 'Veterinary technicians and assistants'),
    ('325', 'Other health associate professionals'),
    ('331', 'Financial and mathematical associate professionals'),
    ('332', 'Sales and purchasing agents and brokers'),
    ('333', 'Business services agents'),
    ('334', 'Administrative and specialized secretaries'),
    ('335', 'Regulatory government associate professionals'),
    ('341', 'Legal, social and religious associate professionals'),
    ('342', 'Sports and fitness workers'),
    ('343', 'Artistic, cultural and culinary associate professionals'),
    ('351', 'Information and communications technology operations '
            'and user support technicians'),
    ('352', 'Telecommunications and broadcasting technicians'),
    ('411', 'General office clerks'),
    ('412', 'Secretaries (general)'),
    ('413', 'Keyboard operators'),
    ('421', 'Tellers, money collectors and related clerks'),
    ('422', 'Client information workers'),
    ('431', 'Numerical clerks'),
    ('432', 'Material-recording and transport clerks'),
    ('441', 'Other clerical support workers'),
    ('511', 'Travel attendants, conductors and guides'),
    ('512', 'Cooks'),
    ('513', 'Waiters and bartenders'),
    ('514', 'Hairdressers, beauticians and related workers'),
    ('515', 'Building and housekeeping supervisors'),
    ('516', 'Other personal services workers'),
    ('521', 'Street and market salespersons'),
    ('522', 'Shop salespersons'),
    ('523', 'Cashiers and ticket clerks'),
    ('524', 'Other sales workers'),
    ('531', "Child care workers and teachers' aides"),
    ('532', 'Personal care workers in health services'),
    ('541', 'Protective services workers'),
    ('611', 'Market gardeners and crop growers'),
    ('612', 'Animal producers'),
    ('613', 'Mixed crop and animal producers'),
    ('621', 'Forestry and related workers'),
    ('622', 'Fishery workers, hunters and trappers'),
    ('631', 'Subsistence crop farmers'),
    ('632', 'Subsistence livestock farmers'),
    ('633', 'Subsistence mixed crop and livestock farmers'),
    ('634', 'Subsistence fishers, hunters, trappers and gatherers'),
    ('711', 'Building frame and related trades workers'),
    ('712', 'Building finishers and related trades workers'),
    ('713', 'Painters, building structure cleaners and related '
            'trades workers'),
    ('721', 'Sheet and structural metal workers, moulders and welders, '
            'and related workers'),
    ('722', 'Blacksmiths, toolmakers and related trades workers'),
    ('723', 'Machinery mechanics and repairers'),
    ('731', 'Handicraft workers'),
    ('732', 'Printing trades workers'),
    ('741', 'Electrical equipment installers and repairers'),
    ('742', 'Electronics and telecommunications installers and repairers'),
    ('751', 'Food processing and related trades workers'),
    ('752', 'Wood treaters, cabinet-makers and related trades workers'),
    ('753', 'Garment and related trades workers'),
    ('754', 'Other craft and related workers'),
    ('811', 'Mining and mineral processing plant operators'),
    ('812', 'Metal processing and finishing plant operators'),
    ('813', 'Chemical and photographic products plant and machine operators'),
    ('814', 'Rubber, plastic and paper products machine operators'),
    ('815', 'Textile, fur and leather products machine operators'),
    ('816', 'Food and related products machine operators'),
    ('817', 'Wood processing and papermaking plant operators'),
    ('818', 'Other stationary plant and machine operators'),
    ('821', 'Assemblers'),
    ('831', 'Locomotive engine drivers and related workers'),
    ('832', 'Car, van and motorcycle drivers'),
    ('833', 'Heavy truck and bus drivers'),
    ('834', 'Mobile plant operators'),
    ('835', "Ships' deck crews and related workers"),
    ('911', 'Domestic, hotel and office cleaners and helpers'),
    ('912', 'Vehicle, window, laundry and other hand cleaning workers'),
    ('921', 'Agricultural, forestry and fishery labourers'),
    ('931', 'Mining and construction labourers'),
    ('932', 'Manufacturing labourers'),
    ('933', 'Transport and storage labourers'),
    ('941', 'Food preparation assistants'),
    ('951', 'Street and related service workers'),
    ('952', 'Street vendors (excluding food)'),
    ('961', 'Refuse workers'),
    ('962', 'Other elementary workers'),
    ('011', 'Commissioned armed forces officers'),
    ('021', 'Non-commissioned armed forces officers'),
    ('031', 'Armed forces occupations, other ranks'),
]


class GistsConfiguration(SingletonModel):
    base_credit = models.PositiveIntegerField(
        default=settings.DEFAULT_BASE_CREDIT)

    target_branch_count = models.PositiveIntegerField(
        default=settings.DEFAULT_TARGET_BRANCH_COUNT,
        validators=[MinValueValidator(1)])
    target_branch_depth = models.PositiveIntegerField(
        default=settings.DEFAULT_TARGET_BRANCH_DEPTH,
        validators=[MinValueValidator(2)])

    experiment_work = models.PositiveIntegerField(
        default=settings.DEFAULT_EXPERIMENT_WORK,
        validators=[MinValueValidator(1)])
    training_work = models.PositiveIntegerField(
        default=settings.DEFAULT_TRAINING_WORK,
        validators=[MinValueValidator(1)])

    reading_span_words_count = models.PositiveSmallIntegerField(
        default=settings.DEFAULT_READING_SPAN_WORDS_COUNT,
        validators=[MinValueValidator(3)])
    reading_span_trials_count = models.PositiveSmallIntegerField(
        default=settings.DEFAULT_READING_SPAN_TRIALS_COUNT,
        validators=[MinValueValidator(3)])

    @property
    def tree_cost(self):
        return self.target_branch_count * self.target_branch_depth

    def __unicode__(self):
        return "Gists Configuration"

    class Meta:
        verbose_name = "Gists Configuration"


class Sentence(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    tree = models.ForeignKey('Tree', related_name='sentences')
    profile = models.ForeignKey('Profile', related_name='sentences')
    parent = models.ForeignKey('Sentence', related_name='children', null=True)
    tree_as_root = models.OneToOneField('Tree', related_name='root', null=True)
    text = models.CharField(max_length=5000)
    time_used = models.FloatField(validators=[MinValueValidator(0)])
    time_allotted = models.FloatField(validators=[MinValueValidator(0)])
    language = models.CharField(choices=LANGUAGE_CHOICES, max_length=100)
    bucket = models.CharField(choices=BUCKET_CHOICES, max_length=100)

    class Meta:
        ordering = ('-created',)

    @property
    def time_proportion(self):
        return (0.0 if self.time_allotted == 0
                else self.time_used / self.time_allotted)

    def __str__(self):
        max_length = 20
        length = len(self.text)
        trunc, post = ((max_length - 3, '...') if length > max_length
                       else (length, ''))
        string = "{} by '{}': '{}'".format(
            self.id, self.profile.user.username, self.text[:trunc] + post)
        return string


class Tree(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    profiles = models.ManyToManyField('Profile', through='Sentence',
                                      through_fields=('tree', 'profile'),
                                      related_name='trees')

    @property
    def network_edges(self):
        edges = self.sentences.values('pk', 'children')
        return [{'source': e['pk'], 'target': e['children']} for e in edges
                if e['pk'] is not None and e['children'] is not None]

    @property
    def shortest_branch_depth(self):
        # No root or nothing but root? Return fast
        sentences_count = self.sentences.count()
        if sentences_count <= 1:
            return sentences_count

        edges = [(e['source'], e['target']) for e in self.network_edges]
        graph = nx.DiGraph(edges)
        heads = self.root.children.values_list('pk', flat=True)
        all_depths = [nx.single_source_shortest_path_length(graph, h)
                      for h in heads]
        branch_depths = [1 + max(depths.values()) for depths in all_depths]
        return min(branch_depths)

    @property
    def distinct_profiles(self):
        return self.profiles.distinct()


class Profile(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField('auth.User')

    mothertongue = models.CharField(choices=LANGUAGE_CHOICES, max_length=100)
    trained_reformulations = models.BooleanField(default=False)

    introduced_exp_home = models.BooleanField(default=False)
    introduced_exp_play = models.BooleanField(default=False)
    introduced_play_home = models.BooleanField(default=False)
    introduced_play_play = models.BooleanField(default=False)

    @property
    def distinct_trees(self):
        return self.trees.distinct()

    @property
    def suggestion_credit(self):
        config = GistsConfiguration.get_solo()
        base = config.base_credit
        cost = config.tree_cost

        n_created = self.sentences.filter(parent=None).count()
        n_transformed = self.sentences.count() - n_created

        return base + (n_transformed // cost) - n_created

    @property
    def next_credit_in(self):
        config = GistsConfiguration.get_solo()
        cost = config.tree_cost

        n_created = self.sentences.filter(parent=None).count()
        n_transformed = self.sentences.count() - n_created

        return cost - (n_transformed % cost)

    @property
    def reformulations_count(self):
        n_created = self.sentences.filter(parent=None).count()
        return self.sentences.count() - n_created


class Questionnaire(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    profile = models.OneToOneField('Profile')

    age = models.PositiveSmallIntegerField(validators=[MinValueValidator(3),
                                                       MaxValueValidator(120)])
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES)

    naive = models.BooleanField(default=True)
    naive_detail = models.CharField(max_length=500, blank=True, default="")

    isco_major = models.CharField(max_length=5, choices=ISCO_MAJOR_CHOICES)
    isco_submajor = models.CharField(max_length=5,
                                     choices=ISCO_SUBMAJOR_CHOICES)
    isco_minor = models.CharField(max_length=5, choices=ISCO_MINOR_CHOICES)
    isco_freetext = models.CharField(max_length=500, blank=True, default="")


class ReadingSpan(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    profile = models.OneToOneField('Profile', related_name="reading_span")
    words_count = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(3)])
    span = models.FloatField(validators=[MinValueValidator(0)])
