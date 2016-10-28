from starwars_api.client import SWAPIClient
from starwars_api.exceptions import SWAPIClientError

api_client = SWAPIClient()

class BaseModel(object):

    def __init__(self, json_data):
        """
        Dynamically assign all attributes in `json_data` as instance
        attributes of the Model.
        """
        for attr, data in json_data.items():
            setattr(self, attr, data)

    @classmethod
    def get(cls, resource_id):
        """
        Returns an object of current Model requesting data to SWAPI using
        the api_client.
        """
        if cls.RESOURCE_NAME == 'people':
            json_data = api_client.get_people(resource_id)
            return People(json_data)
        elif cls.RESOURCE_NAME == 'films':
            json_data = api_client.get_films(resource_id)
            return Films(json_data)

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """
        if cls.RESOURCE_NAME == 'people':
            return PeopleQuerySet()
        elif cls.RESOURCE_NAME == 'films':
            return FilmsQuerySet()
        

class People(BaseModel):
    """Representing a single person"""
    RESOURCE_NAME = 'people'

    def __init__(self, json_data):
        super(People, self).__init__(json_data)

    def __repr__(self):
        return 'Person: {0}'.format(self.name)


class Films(BaseModel):
    RESOURCE_NAME = 'films'

    def __init__(self, json_data):
        super(Films, self).__init__(json_data)

    def __repr__(self):
        return 'Film: {0}'.format(self.title)


class BaseQuerySet(object):

    def __init__(self):
        self.next_page = None
        self.previous_page = None
        self.results = []
        self.current_record = 0
        self.current_page = 0

    def __iter__(self):
        return self

    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """
        while True:
            if not self.results:
                self.current_page += 1
                self.fetch_data(self.current_page)
                self.current_record = 0
            try:
                return_data = self.results[self.current_record]
            except IndexError:
                self.current_page += 1
                try:
                    self.fetch_data(self.current_page)
                except SWAPIClientError:
                    raise StopIteration
                self.current_record = 0
                return_data = self.results[self.current_record]
            self.current_record += 1
            if self.RESOURCE_NAME == 'people':
                return People(return_data)
            elif self.RESOURCE_NAME == 'films':
                return Films(return_data)
        
    next = __next__
    
    def fetch_data(self, page_number = 1):
        if self.RESOURCE_NAME == 'people':
            json_data = api_client.get_people(**{'page': page_number})
        elif self.RESOURCE_NAME == 'films':
            json_data = api_client.get_films(**{'page': page_number})
            
        self.count = json_data['count']
        self.next_page = json_data['next']
        self.previous_page = json_data['previous']
        self.results = json_data['results']

    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
        _total = 0
        for i in self:
            _total += 1
        return _total


class PeopleQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'people'

    def __init__(self):
        super(PeopleQuerySet, self).__init__()

    def __repr__(self):
        return 'PeopleQuerySet: {0} objects'.format(str(len(self.objects)))


class FilmsQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'films'

    def __init__(self):
        super(FilmsQuerySet, self).__init__()

    def __repr__(self):
        return 'FilmsQuerySet: {0} objects'.format(str(len(self.objects)))
