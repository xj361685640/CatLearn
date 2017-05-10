import sqlite3
import numpy as np


class DescriptorDatabase(object):
    """ Class to store sets of descriptors for a given atoms object assigned a
        unique ID.

        Parameters
        ----------
        db_name : str
            Name of the sqlite database to connect. Default is
            descriptor_store.sqlite.
        table : str
            Name of the table in which to store the descriptors. Default is
            Descriptors.
    """
    def __init__(self, db_name='descriptor_store.sqlite', table='Descriptors'):
        self.db_name = db_name
        self.table = table

    def create_db(self, names):
        """ Function to setup a database storing descriptors.

            Parameters
            ----------
            names : list
                List of heading names for features and targets.
        """
        # Attach database
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cstring = 'uuid text'
        for i in names:
            cstring += ', %s float' % i

        # Create a table
        cursor.execute("""CREATE TABLE IF NOT EXISTS %(table)s (%(cstring)s)"""
                       % {'table': self.table, 'cstring': cstring})

    def create_column(self, new_column):
        """ Function to create a new column in the table. Will be full of None
            values.

            new_column : str
                Name of new feature or target.
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        for c in new_column:
            cursor.execute("alter table %(table)s add column %(new_column)s \
                           'float'" % {'table': self.table, 'new_column': c})
            conn.commit()
        cursor.close()

    def fill_db(self, descriptor_names, data):
        """ Function to fill the descriptor database.

            Parameters
            ----------
            descriptor_names : list
                List of descriptor names for features and targets.
            data : array
                First row should contain string of UUIDs, thereafter array
                should contain floats corresponding to the descriptor names
                provided.
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        qm = '(?'
        for i in range(len(descriptor_names)):
            qm += ',?'
        qm += ')'

        cursor.executemany("INSERT INTO %(table)s VALUES %(qm)s"
                           % {'table': self.table, 'qm': qm}, data)
        conn.commit()

    def update_descriptor(self, descriptor, new_data, unique_id):
        """ Function to update a descriptor based on a given uuid.

            Parameters
            ----------
            descriptor : str
                Name of descriptor to be updated.
            new_data : float
                New value to be entered into table.
            unique_id : str
                The UUID of the entry to be updated.
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        sql = """
        UPDATE %(table)s
        SET %(descriptor)s = %(new_data)s
        WHERE uuid = '%(unique_id)s'
        """ % {'table': self.table, 'descriptor': descriptor,
               'new_data': str(new_data), 'unique_id': unique_id}
        cursor.execute(sql)
        conn.commit()

    def query_db(self, unique_id=None, names=None):
        """ Return single row based on uuid or all rows.

            Parameters
            ----------
            unique_id : str
                If specified, the data corresponding to the given UUID will
                be returned. If None, all rows will be returned.
            names : list
                If specified, only the data corresponding to the provided
                feature/target names will be returned. If None, all columns
                will be returned.
        """
        if names is None:
            names = '*'
        else:
            d = names[0]
            if len(names) > 1:
                for i in names[1:]:
                    d += ', %s' % i
            names = d

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        data = []
        if unique_id is None:
            for row in cursor.execute("SELECT %(desc)s FROM %(table)s"
                                      % {'desc': names, 'table': self.table}):
                data.append(row)
        else:
            sql = "SELECT %(desc)s FROM %(table)s WHERE uuid=?" \
             % {'desc': names, 'table': self.table}
            cursor.execute(sql, [('%s' % unique_id)])
            data = cursor.fetchall()[0]

        return np.asarray(data)

    def get_column_names(self):
        """ Function to get the of a supplied table column names. """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.execute('select * from %s' % self.table)

        return [description[0] for description in cursor.description]
