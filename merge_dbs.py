import sys
import json
import argparse
import copy


class Merger:

    MODELS = [
        ("auth.user",
         ["password", "last_login", "is_superuser", "username", "first_name",
          "last_name", "email", "is_staff", "is_active", "date_joined",
          "groups", "user_permissions"]),
        ("account.emailaddress",
         ["user", "email", "verified", "primary"]),
        ("sites.site",
         ["domain", "name"]),
        ("gists.gistsconfiguration",
         ["target_branch_depth", "target_branch_count", "branch_probability",
          "read_factor", "write_factor", "min_tokens", "pause_period",
          "jabberwocky_mode", "heartbeat", "heartbeat_margin",
          "experiment_work", "training_work", "base_credit"]),
        ("gists.profile",
         ["created", "user", "mothertongue", "trained_reformulations",
          "introduced_exp_home", "introduced_exp_play", "introduced_play_home",
          "introduced_play_play", "prolific_id"]),
        ("gists.tree",
         ["created", "profile_lock", "profile_lock_heartbeat"]),
        ("gists.sentence",
         ["created", "tree", "profile", "parent", "tree_as_root", "text",
          "read_time_proportion", "read_time_allotted",
          "write_time_proportion", "write_time_allotted", "language",
          "bucket"]),
        ("gists.comment",
         ["created", "profile", "email", "meta", "text"]),
        ("gists.questionnaire",
         ["created", "profile", "age", "gender", "informed", "informed_how",
          "informed_what", "education_level", "education_freetext", "job_type",
          "job_freetext"]),
    ]

    def __init__(self, dbs):
        self.dbs = dbs
        self.pks = dict((model, []) for model, _ in self.MODELS)
        self.merged_db = []

    def _check_dbs(self):
        model_fields = dict(self.MODELS)
        known_models = set(model_fields.keys())

        # Check the models in the dbs are exactly what we know how to process
        for db in self.dbs:
            assert set([inst["model"] for inst in db]) == known_models
            # Check the fields are exactly the ones we know. A better solution
            # would be to check the version of spreadr with which the dbs were
            # created, or the migrations applied, but we have no access to that
            # (migrations aren't exposed by `python manage.py dumpdata ...`).
            for inst in db:
                assert set(inst["fields"].keys()) == \
                    set(model_fields[inst["model"]])

    def merge_dbs(self):
        self._check_dbs()

        for model, _ in self.MODELS:
            getattr(self, model.replace('.', '_'))()

    def _iter_models(self, name):
        def db_instances(db):
            return sorted([inst for inst in db if inst['model'] == name],
                          key=lambda i: i['pk'])

        for db in self.dbs:
            yield db_instances(db)

    def _flatten_values(cls, list_dicts):
        return [value for subdict in list_dicts for value in subdict.values()]

    def _merge_singleton(self, name):
        solo = None

        for db_instances in self._iter_models(name):
            # Check there's only one instance per db
            assert len(db_instances) == 1
            db_instance = db_instances[0]

            # Check all instances match the first one we saw
            if solo is None:
                solo = db_instance
            else:
                assert solo == db_instance

        # Save the one instance
        self.merged_db.append(solo)

    def _merge_model(self, name, foreign_keys={}, preprocess=None):
        assert len(self.pks[name]) == 0

        for i, db_instances in enumerate(self._iter_models(name)):
            db_pks = {}
            self.pks[name].append(db_pks)

            for inst in db_instances:
                inst_copy = copy.deepcopy(inst)

                # Preprocess and skip instance if asked to
                if preprocess is not None:
                    inst_copy = preprocess(inst_copy)
                    if inst_copy is None:
                        continue

                # Update all non-null foreign keys
                for fkey, ftype in foreign_keys.items():
                    if inst['fields'][fkey] is not None:
                        inst_copy['fields'][fkey] = \
                            self.pks[ftype][i][inst['fields'][fkey]]

                # Update pk
                flat_pks = self._flatten_values(self.pks[name])
                if inst_copy['pk'] in flat_pks:
                    inst_copy['pk'] = max(flat_pks) + 1
                db_pks[inst['pk']] = inst_copy['pk']

                # Save the instance
                self.merged_db.append(inst_copy)

    def auth_user(self):
        usernames_lower = set()

        def dedup_username(user):
            username = user['fields']['username']
            user_copy = copy.deepcopy(user)

            if username.lower() in usernames_lower:
                # Find a new unique username
                original_username = username
                dup = 0
                while username.lower() in usernames_lower:
                    dup += 1
                    username = original_username + '__dup_{}'.format(dup)

                # Record the change
                print("Duplicate user '{}', updating username to '{}'"
                      .format(original_username, username))
                user_copy['fields']['username'] = username

            usernames_lower.add(username.lower())
            return user_copy

        self._merge_model('auth.user', preprocess=dedup_username)

    def account_emailaddress(self):
        emails_lower = set()

        def skip_dup_email(emailaddress):
            email = emailaddress['fields']['email']
            if email.lower() in emails_lower:
                # Skip duplicate addresses
                print("Duplicate email '{}', skipping it".format(email))
                return None

            emails_lower.add(email.lower())
            return emailaddress

        self._merge_model('account.emailaddress',
                          foreign_keys={'user': 'auth.user'},
                          preprocess=skip_dup_email)

    def sites_site(self):
        self._merge_singleton('sites.site')

    def gists_gistsconfiguration(self):
        self._merge_singleton('gists.gistsconfiguration')

    def gists_profile(self):
        self._merge_model('gists.profile',
                          foreign_keys={'user': 'auth.user'})

    def gists_tree(self):
        self._merge_model('gists.tree',
                          foreign_keys={'profile_lock': 'gists.profile'})

    def gists_sentence(self):
        self._merge_model('gists.sentence',
                          foreign_keys={'tree': 'gists.tree',
                                        'tree_as_root': 'gists.tree',
                                        'parent': 'gists.sentence',
                                        'profile': 'gists.profile'})

    def gists_comment(self):
        self._merge_model('gists.comment',
                          foreign_keys={'profile': 'gists.profile'})

    def gists_questionnaire(self):
        self._merge_model('gists.questionnaire',
                          foreign_keys={'profile': 'gists.profile'})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Merge two or more databases '
                                     'representing batches of the same '
                                     'experiment.')
    parser.add_argument('--outfile', type=argparse.FileType('w'),
                        default=sys.stdout,
                        help='output file for the merged json database; '
                        'defaults to stdout')
    parser.add_argument('files', metavar='DB_FILE', nargs='+',
                        type=argparse.FileType('r'),
                        help='a json file of one of the databases to merge')
    args = parser.parse_args()

    dbs = []
    for file in args.files:
        dbs.append(json.load(file))

    # Merge databases
    merger = Merger(dbs)
    merger.merge_dbs()

    # Write the output
    json.dump(merger.merged_db, args.outfile, indent=2)
