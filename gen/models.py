from django.db import models
from django.db.models import Q


def initials(words=[]) -> str:
    """
    Returns initials, i.e. takes first letter of each word in the incoming list,
    capitalizes it and adds a point after it.
    """
    init = ''
    for word in words:
        if word:
            init += list(word)[0].upper()
            init += '.'
    return init


class Person(models.Model):
    """
    class for persons in genealogy tree
    """
    title = 'Личность'
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Дата создания',
                                      )
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name='Дата обновления',
                                      )

    lastname = models.CharField(max_length=30,
                                verbose_name='Фамилия',
                                blank=True,
                                null=True,
                                default=''
                                )
    maidenname = models.CharField(max_length=30,
                                verbose_name='Предыдущая фамилия',
                                blank=True,
                                null=True,
                                default=''
                                )
    firstname = models.CharField(max_length=30,
                                 verbose_name='Имя',
                                 blank=True,
                                 null=True,
                                 default=''
                                 )
    middlename = models.CharField(max_length=30,
                                  verbose_name='Отчество',
                                  blank=True,
                                  null=True,
                                  default='')
    sex = models.CharField(max_length=8, choices=[('f', 'женский'), ('m', 'мужской')], default='f')
    birthdate = models.DateField(verbose_name='Дата рождения',
                                 blank=True,
                                 null=True
                                 )
    date_of_death = models.DateField(verbose_name='Дата смерти',
                                     blank=True,
                                     null=True
                                     )
    place_of_birth = models.CharField(max_length=128,
                                      verbose_name='Место рождения',
                                      blank=True,
                                      null=True,
                                      default=''
                                      )
    birth_marriage = models.ForeignKey('Marriage',
                                       on_delete=models.PROTECT,
                                       verbose_name='Родительский союз',
                                       related_name='child',
                                       blank=True,
                                       null=True)

    def __str__(self):
        return f"{self.lastname} {self.firstname} {self.middlename}, {self.birthdate.year} г.р."

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('personview', args=[str(self.pk)])

    def get_spouses(self):
        """
        Returns a list of all spouses of the person
        """
        spouses = []
        if self.sex == 'm':
            qs = Marriage.objects.filter(husband__pk=self.pk)
            for item in qs:
                spouses.append(item.wife)
        else:
            qs = Marriage.objects.filter(wife__pk=self.pk)
            for item in qs:
                spouses.append(item.husband)
        return spouses

    def get_marriages(self):
        """
        Returns a query with all marriages of the person
        """
        marriages = Marriage.objects.filter(Q(husband__pk=self.pk) | Q(wife__pk=self.pk)).order_by('date')

        return marriages

    def get_marriages_with_spouses(self):
        """
        Returns a list of all marriages of the person together with its spouse
        [[marriage, spouse],[marriage, spouse],]
        """
        qs = self.get_marriages()
        marriages = []
        for item in qs:
            spouse = item.husband if item.wife.pk==self.pk else item.wife
            marriages.append([item, spouse])

        return marriages

    def get_children(self):
        """
        Returns a list of all children of the person
        """
        marriages = Marriage.objects.filter(Q(husband__pk=self.pk) | Q(wife__pk=self.pk)).order_by('date')
        all_children = []
        for item in marriages:
            children = item.child.all()
            if children:
                for c in children:
                    all_children.append(c)

        return all_children

    def get_parents(self):
        """
        Returns a dict with parents of the person
        """
        parents_marriage = self.birth_marriage
        parents = {}
        if parents_marriage:
            parents = {'father': parents_marriage.husband, 'mother': parents_marriage.wife}

        return parents


class Marriage(models.Model):
    """
    class for marriage (official, civil or church)
    """
    title = 'Marriage'
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name='Дата обновления')

    date = models.DateField(verbose_name='Дата заключения',
                            blank=True,
                            null=True
                            )
    date_of_divorce = models.DateField(verbose_name='Дата расторжения',
                                       blank=True,
                                       null=True
                                       )
    husband = models.ForeignKey(Person, on_delete=models.PROTECT, related_name='husband')
    wife = models.ForeignKey(Person, on_delete=models.PROTECT, related_name='wife')

    class Meta:
        unique_together = ['husband', 'wife']

    def __str__(self):
        husband_initials = self.husband.lastname + ' ' + initials([self.husband.firstname, self.husband.middlename])
        if self.wife.maidenname:
            wife_initials = f"{self.wife.lastname} ({self.wife.maidenname})"
        else:
            wife_initials = f"{self.wife.lastname}"
        wife_initials += ' ' + initials([self.wife.firstname, self.wife.middlename])
        return f"{husband_initials} - {wife_initials}, {self.date.year}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('marriageview', args=[str(self.pk)])

    def get_children(self):
        """
        Returns a list of all children of the marriage
        """
        children = self.child.all()
        all_children = []
        if children:
            for c in children:
                all_children.append(c)

        return all_children