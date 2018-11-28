from app import helper


def transformGeo(geometry,toCRS):
    return 'st_transform(st_geomfromtext(\''+ geometry +'\'::text,4326),' + toCRS + ')'



def vector_query(scalevalue,vector_table_requested, geometry,toCRS):
    """
    this function will return the need scale query select the scalevalue
    :param scalevalue:
    :param vector_table_requested:
    :param geometry:
    :param toCRS:
    :return: the right query select the scalevalue
    """
    if scalevalue == 'hectare':
        return vector_query_hectares(vector_table_requested, geometry,toCRS)
    elif scalevalue == 'nuts':
        id_selected_list = helper.adapt_nuts_list(geometry)
        return vector_query_nuts(vector_table_requested, id_selected_list)
    elif scalevalue == 'lau':
        id_selected_list = helper.adapt_nuts_list(geometry)
        return vector_query_lau(vector_table_requested, id_selected_list,toCRS)
    return None



def vector_query_hectares(vector_table_requested, geometry,toCRS):
    """
    this function will return an array of the vector table selected at hectares
    :param vector_table_requested:
    :param geometry:
    :param toCRS:
    :return:
    """

    query= "with subAreas as ( SELECT nuts.nuts_id FROM geo.nuts " + \
           "where ST_Intersects( nuts.geom," + \
           " "+transformGeo(geometry,toCRS)+" ) "  + \
           "AND STAT_LEVL_ = 0 AND year = to_date('2013', 'YYYY') ) " + \
           "select * from stat." + vector_table_requested + ",subAreas " + \
           "where nuts0_id = subAreas.nuts_id"

    return query

def vector_query_nuts(vector_table_requested, area_selected):
    """
    this function will return an array of the vector table selected from a selection at hectare level
    :param vector_table_requested:
    :param geometry:
    :return:
    """
    vector_table_requested = str(vector_table_requested)
    query= "with selected_zone as ( SELECT geom as geom from geo.nuts where nuts_id IN("+ area_selected+") " \
                                                                                                        "AND year = to_date('2013', 'YYYY') ), subAreas as ( SELECT distinct geo.nuts.nuts_id " \
                                                                                                        "FROM selected_zone, geo.nuts where ST_Intersects( geo.nuts.geom, selected_zone.geom ) " \
                                                                                                        "AND geo.nuts.STAT_LEVL_ = 0 AND geo.nuts.year = to_date('2013', 'YYYY') ) " \
                                                                                                        "select * from stat." + vector_table_requested + ",subAreas where nuts0_id = subAreas.nuts_id"

    return query


def vector_query_lau(vector_table_requested, area_selected,toCRS):
    """
    this function will return an array of the vector table selected from a selection at lau level
    :param vector_table_requested:
    :param geometry:
    :return
    """

    query= "with selected_zone as ( SELECT ST_Transform(geom,"+ toCRS +") as geom" \
                                                                       " from geo.lau where comm_id IN("+ area_selected+") AND year = to_date('2013', 'YYYY') )," \
                                                                                                                        " subAreas as ( SELECT distinct geo.nuts.nuts_id FROM selected_zone, geo.nuts " \
                                                                                                                        "where ST_Intersects( geo.nuts.geom, selected_zone.geom ) AND geo.nuts.STAT_LEVL_ = 0 " \
                                                                                                                        "AND geo.nuts.year = to_date('2013', 'YYYY') ) select * from stat." + vector_table_requested + ",subAreas where nuts0_id = subAreas.nuts_id"

    return query

