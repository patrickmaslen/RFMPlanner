##############################################################################################
###     Functions listed in alphabetical order, except for domain creation (at end of file)
##############################################################################################


def assemble_report_data_bkp():
    # Used where no spatially varying thresholds
    return """
    DROP VIEW IF EXISTS region_summary_report_data;
    DROP TABLE IF EXISTS region_underlying_report_data;
    
    CREATE TABLE region_underlying_report_data(fma_type, fuel_type, threshold_age, yslb, target, geometry) AS
    SELECT rfc.fma_type, t.fuel_type, lkp.threshold_age, t.yslb, lkp.target,
    (ST_Dump(PolygonalIntersection(ST_Buffer(rfc.geometry, 0.001), ST_Buffer(t.geometry, 0.001)))).geom AS geometry
    FROM region_fmas_complete rfc, region_fuel_type_age t JOIN region_fuel_fma_thold_target_lookup lkp
    ON t.fuel_type = lkp.fuel_type
    WHERE rfc.fma_type = 'SHS' AND lkp.fma = 'SHS'
    AND ST_Intersects(rfc.geometry, t.geometry) 
    AND NOT  ST_Touches(rfc.geometry, t.geometry)
    UNION
    SELECT rfc.fma_type, t.fuel_type, lkp.threshold_age, t.yslb, lkp.target,
    (ST_Dump(PolygonalIntersection(ST_Buffer(rfc.geometry, 0.001), ST_Buffer(t.geometry, 0.001)))).geom AS geometry
    FROM region_fmas_complete rfc, region_fuel_type_age t JOIN region_fuel_fma_thold_target_lookup lkp
    ON t.fuel_type = lkp.fuel_type
    WHERE rfc.fma_type = 'CIB' AND lkp.fma = 'CIB'
    AND ST_Intersects(rfc.geometry, t.geometry) 
    AND NOT ST_Touches(rfc.geometry, t.geometry)
    UNION
    SELECT rfc.fma_type, t.fuel_type, lkp.threshold_age, t.yslb, lkp.target,
    (ST_Dump(PolygonalIntersection(ST_Buffer(rfc.geometry, 0.001), ST_Buffer(t.geometry, 0.001)))).geom AS geometry
    FROM region_fmas_complete rfc, region_fuel_type_age t JOIN region_fuel_fma_thold_target_lookup lkp
    ON t.fuel_type = lkp.fuel_type
    WHERE rfc.fma_type = 'LRR' AND lkp.fma = 'LRR'
    AND ST_Intersects(rfc.geometry, t.geometry) 
    AND NOT ST_Touches(rfc.geometry, t.geometry);
    
    CREATE TRIGGER trig_region_underlying_report_data_update 
    AFTER INSERT OR UPDATE OR DELETE ON region_underlying_report_data
    FOR EACH STATEMENT
    EXECUTE PROCEDURE update_table_updates();
    
    DELETE FROM table_updates WHERE table_name = 'region_underlying_report_data';
    INSERT INTO table_updates VALUES('region_underlying_report_data', CURRENT_TIMESTAMP AT TIME ZONE 'australia/west');
    
    CREATE VIEW region_summary_report_data AS
    SELECT 'region' AS xxx , fma_type, target, CASE WHEN yslb >= threshold_age THEN TRUE ELSE FALSE END AS reached_th, SUM(ST_Area(geometry))/10000 AS area_ha
    FROM region_underlying_report_data
    GROUP BY xxx, fma_type, target, reached_th;
    """

def assemble_report_data():
    # Used where no spatially varying thresholds
    # 'name' is replaced in rfm_libary code with either region name or asset name
    return """
    DROP VIEW IF EXISTS name_summary_report_data;
    DROP TABLE IF EXISTS name_underlying_report_data;
    
    CREATE TABLE name_underlying_report_data(fma_type, fuel_type, threshold_age, yslb, target, geometry) AS
    SELECT rfc.fma_type, t.fuel_type, lkp.threshold_age, t.yslb, lkp.target,
    (ST_Dump(PolygonalIntersection(ST_Buffer(rfc.geometry, 0.001), ST_Buffer(t.geometry, 0.001)))).geom AS geometry
    FROM name_fmas_complete rfc, region_fuel_type_age t JOIN region_fuel_fma_thold_target_lookup lkp
    ON t.fuel_type = lkp.fuel_type
    WHERE rfc.fma_type = 'SHS' AND lkp.fma = 'SHS'
    AND ST_Intersects(rfc.geometry, t.geometry) 
    AND NOT  ST_Touches(rfc.geometry, t.geometry)
    UNION
    SELECT rfc.fma_type, t.fuel_type, lkp.threshold_age, t.yslb, lkp.target,
    (ST_Dump(PolygonalIntersection(ST_Buffer(rfc.geometry, 0.001), ST_Buffer(t.geometry, 0.001)))).geom AS geometry
    FROM name_fmas_complete rfc, region_fuel_type_age t JOIN region_fuel_fma_thold_target_lookup lkp
    ON t.fuel_type = lkp.fuel_type
    WHERE rfc.fma_type = 'CIB' AND lkp.fma = 'CIB'
    AND ST_Intersects(rfc.geometry, t.geometry) 
    AND NOT ST_Touches(rfc.geometry, t.geometry)
    UNION
    SELECT rfc.fma_type, t.fuel_type, lkp.threshold_age, t.yslb, lkp.target,
    (ST_Dump(PolygonalIntersection(ST_Buffer(rfc.geometry, 0.001), ST_Buffer(t.geometry, 0.001)))).geom AS geometry
    FROM name_fmas_complete rfc, region_fuel_type_age t JOIN region_fuel_fma_thold_target_lookup lkp
    ON t.fuel_type = lkp.fuel_type
    WHERE rfc.fma_type = 'LRR' AND lkp.fma = 'LRR'
    AND ST_Intersects(rfc.geometry, t.geometry) 
    AND NOT ST_Touches(rfc.geometry, t.geometry);
    
    CREATE TRIGGER trig_name_underlying_report_data_update 
    AFTER INSERT OR UPDATE OR DELETE ON name_underlying_report_data
    FOR EACH STATEMENT
    EXECUTE PROCEDURE update_table_updates();
    
    DELETE FROM table_updates WHERE table_name = 'name_underlying_report_data';
    INSERT INTO table_updates VALUES('name_underlying_report_data', CURRENT_TIMESTAMP AT TIME ZONE 'australia/west');
    
    CREATE VIEW name_summary_report_data AS
    SELECT 'region' AS xxx , fma_type, target, CASE WHEN yslb >= threshold_age THEN TRUE ELSE FALSE END AS reached_th, SUM(ST_Area(geometry))/10000 AS area_ha
    FROM name_underlying_report_data
    GROUP BY xxx, fma_type, target, reached_th;
    """

def assemble_report_data_spatial_tholds_part_1():
    # Applied to fuel_types with no records in region_spatial_thresholds
    return """
    DROP VIEW IF EXISTS name_summary_report_data;
    DROP TABLE IF EXISTS name_underlying_report_data;
    
    CREATE TABLE name_underlying_report_data(fma_type, fuel_type, threshold_age, yslb, target, geometry) AS
    SELECT rfc.fma_type, t.fuel_type, lkp.threshold_age, t.yslb, lkp.target,
    (ST_Dump(PolygonalIntersection(ST_Buffer(rfc.geometry, 0.001), ST_Buffer(t.geometry, 0.001)))).geom AS geometry
    FROM name_fmas_complete rfc, region_fuel_type_age t JOIN region_fuel_fma_thold_target_lookup lkp
    ON t.fuel_type = lkp.fuel_type
    WHERE rfc.fma_type = 'SHS' AND lkp.fma = 'SHS' AND t.fuel_type NOT IN (fuel_types_w_spatial_tholds)
    AND ST_Intersects(rfc.geometry, t.geometry) 
    AND NOT  ST_Touches(rfc.geometry, t.geometry)
    UNION
    SELECT rfc.fma_type, t.fuel_type, lkp.threshold_age, t.yslb, lkp.target,
    (ST_Dump(PolygonalIntersection(ST_Buffer(rfc.geometry, 0.001), ST_Buffer(t.geometry, 0.001)))).geom AS geometry
    FROM name_fmas_complete rfc, region_fuel_type_age t JOIN region_fuel_fma_thold_target_lookup lkp
    ON t.fuel_type = lkp.fuel_type
    WHERE rfc.fma_type = 'CIB' AND lkp.fma = 'CIB' AND t.fuel_type NOT IN (fuel_types_w_spatial_tholds)
    AND ST_Intersects(rfc.geometry, t.geometry) 
    AND NOT  ST_Touches(rfc.geometry, t.geometry)
    UNION
    SELECT rfc.fma_type, t.fuel_type, lkp.threshold_age, t.yslb, lkp.target,
    (ST_Dump(PolygonalIntersection(ST_Buffer(rfc.geometry, 0.001), ST_Buffer(t.geometry, 0.001)))).geom AS geometry
    FROM name_fmas_complete rfc, region_fuel_type_age t JOIN region_fuel_fma_thold_target_lookup lkp
    ON t.fuel_type = lkp.fuel_type
    WHERE rfc.fma_type = 'LRR' AND lkp.fma = 'LRR' AND t.fuel_type NOT IN (fuel_types_w_spatial_tholds)
    AND ST_Intersects(rfc.geometry, t.geometry) 
    AND NOT  ST_Touches(rfc.geometry, t.geometry);
    
    CREATE TRIGGER trig_name_underlying_report_data_update 
    AFTER INSERT OR UPDATE OR DELETE ON name_underlying_report_data
    FOR EACH STATEMENT
    EXECUTE PROCEDURE update_table_updates();
    
    DELETE FROM table_updates WHERE table_name = 'name_underlying_report_data';
    INSERT INTO table_updates VALUES('name_underlying_report_data', CURRENT_TIMESTAMP AT TIME ZONE 'australia/west');
    
    CREATE VIEW name_summary_report_data AS
    SELECT 'region' AS xxx , fma_type, target, CASE WHEN yslb >= threshold_age THEN TRUE ELSE FALSE END AS reached_th, SUM(ST_Area(geometry))/10000 AS area_ha
    FROM name_underlying_report_data
    GROUP BY xxx, fma_type, target, reached_th;
    """

def assemble_report_data_spatial_tholds_part_2():
    # Applied to fuel_types WITH record(s) in region_spatial_thresholds
    # Incudes full geometry of fuel_type_age polys which DO NOT INTERSECT spatial thresholds for that veg type
    return """
    INSERT INTO name_underlying_report_data(fma_type, fuel_type, threshold_age, yslb, target, geometry) 
    SELECT rfc.fma_type, t.fuel_type, lkp.threshold_age, t.yslb, lkp.target,
    (ST_Dump(PolygonalIntersection(ST_Buffer(rfc.geometry, 0.001), ST_Buffer(t.geometry, 0.001)))).geom AS geometry
    FROM name_fmas_complete rfc, region_fuel_type_age t JOIN region_fuel_fma_thold_target_lookup lkp 
    ON t.fuel_type = lkp.fuel_type JOIN region_spatial_thresholds sp ON lkp.fuel_type = sp.fuel_type
    WHERE rfc.fma_type = 'SHS' AND lkp.fma = 'SHS' AND t.fuel_type = 'fuel_type_w_spatial_thold'
    AND ST_Intersects(rfc.geometry, t.geometry)
    AND NOT ST_Intersects(t.geometry, sp.geometry);
    
    INSERT INTO name_underlying_report_data(fma_type, fuel_type, threshold_age, yslb, target, geometry) 
    SELECT rfc.fma_type, t.fuel_type, lkp.threshold_age, t.yslb, lkp.target,
    (ST_Dump(PolygonalIntersection(ST_Buffer(rfc.geometry, 0.001), ST_Buffer(t.geometry, 0.001)))).geom AS geometry
    FROM name_fmas_complete rfc, region_fuel_type_age t JOIN region_fuel_fma_thold_target_lookup lkp 
    ON t.fuel_type = lkp.fuel_type JOIN region_spatial_thresholds sp ON lkp.fuel_type = sp.fuel_type
    WHERE rfc.fma_type = 'CIB' AND lkp.fma = 'CIB' AND t.fuel_type = 'fuel_type_w_spatial_thold'
    AND ST_Intersects(rfc.geometry, t.geometry)
    AND NOT ST_Intersects(t.geometry, sp.geometry);
    
    INSERT INTO name_underlying_report_data(fma_type, fuel_type, threshold_age, yslb, target, geometry) 
    SELECT rfc.fma_type, t.fuel_type, lkp.threshold_age, t.yslb, lkp.target,
    (ST_Dump(PolygonalIntersection(ST_Buffer(rfc.geometry, 0.001), ST_Buffer(t.geometry, 0.001)))).geom AS geometry
    FROM name_fmas_complete rfc, region_fuel_type_age t JOIN region_fuel_fma_thold_target_lookup lkp 
    ON t.fuel_type = lkp.fuel_type JOIN region_spatial_thresholds sp ON lkp.fuel_type = sp.fuel_type
    WHERE rfc.fma_type = 'LRR' AND lkp.fma = 'LRR' AND t.fuel_type = 'fuel_type_w_spatial_thold'
    AND ST_Intersects(rfc.geometry, t.geometry)
    AND NOT ST_Intersects(t.geometry, sp.geometry);
    """

def assemble_report_data_spatial_tholds_part_3():
    # Applied to fuel_types WITH record(s) in region_spatial_thresholds
    # Incudes the NON-INTERSECTING part of geometries of fuel_type_age polys which DO intersect spatial thresholds for that veg type
    return """
    INSERT INTO name_underlying_report_data(fma_type, fuel_type, threshold_age, yslb, target, geometry) 
    SELECT rfc.fma_type, t.fuel_type, lkp.threshold_age, t.yslb, lkp.target,
    (ST_Dump(PolygonalIntersection(rfc.geometry, ST_Difference(t.geometry, sp.geometry)))).geom AS geometry
    FROM name_fmas_complete rfc, region_fuel_type_age t JOIN region_fuel_fma_thold_target_lookup lkp 
    ON t.fuel_type = lkp.fuel_type JOIN region_spatial_thresholds sp ON lkp.fuel_type = sp.fuel_type
    WHERE rfc.fma_type = 'SHS' AND lkp.fma = 'SHS' 
    AND t.fuel_type = 'fuel_type_w_spatial_thold' AND lkp.fuel_type = 'fuel_type_w_spatial_thold' AND sp.fuel_type = 'fuel_type_w_spatial_thold'
    AND ST_Intersects(rfc.geometry, t.geometry)
    AND NOT ST_Touches(rfc.geometry, t.geometry)
    AND ST_Overlaps(t.geometry, sp.geometry)
    AND ST_Intersects(rfc.geometry, sp.geometry);
    
    INSERT INTO name_underlying_report_data(fma_type, fuel_type, threshold_age, yslb, target, geometry) 
    SELECT rfc.fma_type, t.fuel_type, lkp.threshold_age, t.yslb, lkp.target,
    (ST_Dump(PolygonalIntersection(ST_Buffer(rfc.geometry, 0), ST_Difference(t.geometry, sp.geometry)))).geom AS geometry
    FROM name_fmas_complete rfc, region_fuel_type_age t JOIN region_fuel_fma_thold_target_lookup lkp 
    ON t.fuel_type = lkp.fuel_type JOIN region_spatial_thresholds sp ON lkp.fuel_type = sp.fuel_type
    WHERE rfc.fma_type = 'CIB' AND lkp.fma = 'CIB' 
    AND t.fuel_type = 'fuel_type_w_spatial_thold' AND lkp.fuel_type = 'fuel_type_w_spatial_thold' AND sp.fuel_type = 'fuel_type_w_spatial_thold'
    AND ST_Intersects(rfc.geometry, t.geometry)
    AND NOT ST_Touches(rfc.geometry, t.geometry)
    AND ST_Overlaps(t.geometry, sp.geometry)
    AND ST_Intersects(rfc.geometry, sp.geometry);
    
    INSERT INTO name_underlying_report_data(fma_type, fuel_type, threshold_age, yslb, target, geometry) 
    SELECT rfc.fma_type, t.fuel_type, lkp.threshold_age, t.yslb, lkp.target,
    (ST_Dump(PolygonalIntersection(ST_Buffer(rfc.geometry, 0), ST_Difference(t.geometry, sp.geometry)))).geom AS geometry
    FROM name_fmas_complete rfc, region_fuel_type_age t JOIN region_fuel_fma_thold_target_lookup lkp 
    ON t.fuel_type = lkp.fuel_type JOIN region_spatial_thresholds sp ON lkp.fuel_type = sp.fuel_type
    WHERE rfc.fma_type = 'LRR' AND lkp.fma = 'LRR' 
    AND t.fuel_type = 'fuel_type_w_spatial_thold' AND lkp.fuel_type = 'fuel_type_w_spatial_thold' AND sp.fuel_type = 'fuel_type_w_spatial_thold'
    AND ST_Intersects(rfc.geometry, t.geometry)
    AND NOT ST_Touches(rfc.geometry, t.geometry)
    AND ST_Overlaps(t.geometry, sp.geometry)
    AND ST_Intersects(rfc.geometry, sp.geometry);
    """

def assemble_report_data_spatial_tholds_part_4():
    # Applied to fuel_types WITH record(s) in region_spatial_thresholds
    # Incudes the INTERSECTING part of geometries of fuel_type_age polys which DO intersect spatial thresholds for that veg type
    return """
    INSERT INTO name_underlying_report_data(fma_type, fuel_type, threshold_age, yslb, target, geometry) 
    SELECT rfc.fma_type, t.fuel_type, sp.threshold_age, t.yslb, sp.shs_target,
    (ST_Dump(PolygonalIntersection(sp.geometry, PolygonalIntersection(ST_Buffer(rfc.geometry, 0), ST_Buffer(t.geometry, 0.001))))).geom AS geometry
    FROM name_fmas_complete rfc, region_fuel_type_age t JOIN region_spatial_thresholds sp ON t.fuel_type = sp.fuel_type
    WHERE rfc.fma_type = 'SHS'
    AND t.fuel_type = 'fuel_type_w_spatial_thold'AND sp.fuel_type = 'fuel_type_w_spatial_thold'
    AND ST_Intersects(rfc.geometry, t.geometry) 
    AND NOT ST_Touches(rfc.geometry, t.geometry)
    AND ST_Intersects(t.geometry, sp.geometry)
    AND NOT ST_Touches(t.geometry, sp.geometry);
    
    INSERT INTO name_underlying_report_data(fma_type, fuel_type, threshold_age, yslb, target, geometry) 
    SELECT rfc.fma_type, t.fuel_type, sp.threshold_age, t.yslb, sp.cib_target,
    (ST_Dump(PolygonalIntersection(sp.geometry, PolygonalIntersection(ST_Buffer(rfc.geometry, 0), ST_Buffer(t.geometry, 0.001))))).geom AS geometry
    FROM name_fmas_complete rfc, region_fuel_type_age t JOIN region_spatial_thresholds sp ON t.fuel_type = sp.fuel_type
    WHERE rfc.fma_type = 'CIB' 
    AND t.fuel_type = 'fuel_type_w_spatial_thold' AND sp.fuel_type = 'fuel_type_w_spatial_thold'
    AND ST_Intersects(rfc.geometry, t.geometry) 
    AND NOT ST_Touches(rfc.geometry, t.geometry)
    AND ST_Intersects(t.geometry, sp.geometry)
    AND NOT ST_Touches(t.geometry, sp.geometry);
    
    INSERT INTO name_underlying_report_data(fma_type, fuel_type, threshold_age, yslb, target, geometry) 
    SELECT rfc.fma_type, t.fuel_type, sp.threshold_age, t.yslb, sp.lrr_target,
    (ST_Dump(PolygonalIntersection(sp.geometry, PolygonalIntersection(ST_Buffer(rfc.geometry, 0), ST_Buffer(t.geometry, 0.001))))).geom AS geometry
    FROM name_fmas_complete rfc, region_fuel_type_age t JOIN region_spatial_thresholds sp ON t.fuel_type = sp.fuel_type
    WHERE rfc.fma_type = 'LRR'
    AND t.fuel_type = 'fuel_type_w_spatial_thold' AND sp.fuel_type = 'fuel_type_w_spatial_thold'
    AND ST_Intersects(rfc.geometry, t.geometry) 
    AND NOT ST_Touches(rfc.geometry, t.geometry)
    AND ST_Intersects(t.geometry, sp.geometry)
    AND NOT ST_Touches(t.geometry, sp.geometry);
    """

def calculate_interim_fmas_combined():
    # called by rfm_library.create_interim
    return """
    DROP TABLE IF EXISTS table_name;
    CREATE TABLE public.table_name
    (id serial primary key,
    fma_type varchar(3),
    priority integer,
    source varchar(10),
    geometry geometry(MultiPolygon, 900914))
    TABLESPACE pg_default;

    DROP INDEX IF EXISTS table_name_spat_idx;
    CREATE INDEX table_name_spat_idx ON table_name USING GIST(geometry);

    ALTER TABLE public.table_name
        OWNER TO rfmp;

    INSERT INTO table_name (fma_type, priority, source, geometry)
    SELECT 
        result.fma_type,
        result.priority,
        result.source,
        ST_Multi(ST_CollectionExtract(ST_MakeValid(result.geometry),3)::geometry(MultiPolygon,900914)) AS geometry
    FROM ( 
    SELECT fma_type, 
            done.priority, 
            'Diff' AS source,
          ST_Multi(ST_CollectionExtract(
                ST_Difference(
                    ST_Buffer(
                        done.geometry, 
                        0),
                    ST_Buffer(
                       ST_Collect(next_in.geometry)
                        , 0)
                )
            , 3))
            AS geometry
    FROM input2 done, input1 next_in
    WHERE ST_Intersects(ST_Buffer(
                            done.geometry, 0),
                        ST_Buffer(
                            next_in.geometry, 0)
                        )
    GROUP BY fma_type, done.priority, done.geometry

    UNION

    SELECT fma_type, 
            done.priority, 
            'Non-int' AS source,
            done.geometry
    FROM input2 done, input1 next_in
    GROUP BY fma_type, done.priority, done.geometry
    HAVING NOT ST_Intersects(ST_Buffer(
                           done.geometry, 0),
                        ST_Buffer(
                            ST_Collect(next_in.geometry), 0)
                        )

    UNION

    SELECT fma as fma_type, priority, 'New' AS source, geometry FROM input1
    ) AS result;
    DELETE FROM table_name WHERE ST_IsEmpty(geometry);
    """

def calculate_interim_fmas_combined_no_prioritisn():
    # called by rfm_library.create_interim
    return """
    DROP TABLE IF EXISTS table_name;
    CREATE TABLE public.table_name
    (id serial primary key,
    fma_type varchar(3),
    source varchar(10),
    geometry geometry(MultiPolygon, 900914))
    TABLESPACE pg_default;

    DROP INDEX IF EXISTS table_name_spat_idx;
    CREATE INDEX table_name_spat_idx ON table_name USING GIST(geometry);

    ALTER TABLE public.table_name
        OWNER TO rfmp;

    INSERT INTO table_name (fma_type, source, geometry)
    SELECT 
        result.fma_type,
        result.source,
        ST_Multi(ST_CollectionExtract(ST_MakeValid(result.geometry),3)::geometry(MultiPolygon,900914)) AS geometry
    FROM (
    SELECT fma_type, 
            'Diff' AS source,
            ST_Multi(ST_CollectionExtract(                
                ST_MakeValid(
                    ST_Difference(
                        ST_Buffer(
                            ST_SnapToGrid(done.geometry, 0.001), 
                            0),
                        ST_Buffer(
                           ST_Collect(ST_SnapToGrid(next_in.geometry, 0.001))
                            , 0)
                    )
                )
            , 3))
            AS geometry
    FROM input2 done, input1 next_in
    WHERE ST_Intersects(done.geometry, next_in.geometry)
    GROUP BY fma_type, done.geometry

    UNION

    SELECT fma_type, 
            'Non-int' AS source,
            done.geometry
    FROM input2 done, input1 next_in
    GROUP BY fma_type, done.geometry
    HAVING NOT ST_Intersects(done.geometry, ST_Collect(next_in.geometry))

    UNION

    SELECT fma as fma_type, 'New' AS source, geometry FROM input1
    ) AS result;
    DELETE FROM table_name WHERE ST_IsEmpty(geometry);
    """    

def calculate_intersects():
    # called by rfm_library.calculate_intersects
    # Made correction 6-Mar-2020; previously had CASE WHEN ... THEN be.geometry and GROUP BY priority, be.geometry
    return """
    INSERT INTO temp_intersect_tbl_name
    SELECT priority, 
            CASE WHEN ST_CoveredBy(ST_CollectionExtract(ST_Collect(buff.geometry), 3), be.geometry) THEN buff.geometry
            ELSE PolygonalIntersection(ST_Union(buff.geometry), be.geometry)
            END
    FROM temp_buffer_tbl_name AS buff, buffer_extents AS be 
    WHERE be.fma_code = 'fma_type' AND be.buffer = buffer_distance AND ST_Intersects(buff.geometry, be.geometry) AND NOT ST_Touches(buff.geometry, be.geometry) 
    GROUP BY priority, be.geometry, buff.geometry;
    DELETE FROM temp_intersect_tbl_name WHERE ST_IsEmpty(geometry);
    """

def create_definitive_threshold_table():
    # called by rfm_library.calculate_defin_tholds
    return """
    DROP VIEW IF EXISTS region_thold_details;
    DROP VIEW IF EXISTS region_past_thold;
    DROP TABLE IF EXISTS region_with_thold;
    DROP INDEX IF EXISTS region_with_thold_spat_idx;
    DROP INDEX IF EXISTS idx_region_with_thold_threshold_age_yslb;
               
    CREATE TABLE public.region_with_thold
    (id serial primary key,
    fma_type varchar(3),
    fuel_type  varchar(19) COLLATE pg_catalog."default",
    target integer,
    threshold_age integer,
    yslb integer,
    geometry geometry(Polygon, 900914))
    TABLESPACE pg_default;

    CREATE INDEX region_with_thold_spat_idx ON region_with_thold USING GIST(geometry);
    CREATE INDEX idx_region_with_thold_threshold_age_yslb
        ON public.region_with_thold USING btree
        (threshold_age, yslb)
        TABLESPACE pg_default;

    ALTER TABLE public.region_with_thold
        OWNER TO rfmp;
        
    CREATE OR REPLACE VIEW region_thold_details as select *, CASE
                WHEN region_with_thold.yslb >= region_with_thold.threshold_age AND region_with_thold.threshold_age > 0 THEN true
                ELSE false
            END AS reached_th 
    FROM region_with_thold;

    CREATE OR REPLACE VIEW region_past_thold AS select *
    FROM region_with_thold
    WHERE region_with_thold.yslb >= region_with_thold.threshold_age AND region_with_thold.threshold_age > 0;
    
    DELETE FROM table_updates WHERE table_name = 'region_with_thold';
    INSERT INTO table_updates VALUES('region_with_thold', CURRENT_TIMESTAMP AT TIME ZONE 'australia/west');
    """

def create_fmas_complete():
    # called by rfm_library.complete_fmas
    return """DROP TABLE IF EXISTS region_fmas_complete;

    CREATE TABLE region_fmas_complete AS 
    SELECT fma_type, priority, ST_Multi(ST_CollectionExtract((ST_Dump(ST_MakeValid(ST_Union(ST_Buffer(geometry, 0))))).geom, 3))::geometry(MultiPolygon,900914) AS geometry
    FROM region_fmas_combined 
    GROUP BY fma_type, priority;

    ALTER TABLE region_fmas_complete ADD COLUMN id SERIAL PRIMARY KEY;

    CREATE INDEX region_fmas_complete_spat_idx ON region_fmas_complete USING GIST (geometry);
    
    DELETE FROM region_fmas_complete WHERE ST_Area(geometry) < 1;

    ANALYZE region_fmas_complete;
    
    CREATE TRIGGER trig_region_fmas_complete_update 
    AFTER INSERT OR UPDATE OR DELETE ON region_fmas_complete
    FOR EACH STATEMENT
    EXECUTE PROCEDURE update_table_updates();
    
    DELETE FROM table_updates WHERE table_name = 'region_fmas_complete';
    INSERT INTO table_updates VALUES('region_fmas_complete', CURRENT_TIMESTAMP AT TIME ZONE 'australia/west');
    """

def create_region_fuel_fma_thold_target_lookup():
    return"""
    DROP VIEW IF EXISTS region_fuel_fma_thold_target_lookup;
    CREATE VIEW region_fuel_fma_thold_target_lookup AS
    SELECT fuel_type, 'SHS' AS fma, threshold_age, shs_target AS target
    FROM region_default_thresholds
    UNION
    SELECT fuel_type, 'CIB', threshold_age, cib_target 
    FROM region_default_thresholds
    UNION
    SELECT fuel_type, 'LRR', threshold_age, lrr_target 
    FROM region_default_thresholds;
    """

def create_region_fuel_fma_thold_target_spatial_lookup():
    return"""
    DROP VIEW IF EXISTS region_fuel_fma_thold_target_spatial_lookup;
    CREATE VIEW region_fuel_fma_thold_target_spatial_lookup AS
    SELECT fuel_type, 'SHS' AS fma, threshold_age, shs_target AS target, geometry
    FROM region_spatial_thresholds
    UNION
    SELECT fuel_type, 'CIB', threshold_age, cib_target, geometry
    FROM region_spatial_thresholds
    UNION
    SELECT fuel_type, 'LRR', threshold_age, lrr_target, geometry
    FROM region_spatial_thresholds;
    """

def create_region_fuel_type_age_with_thold():
    return """
    DROP TABLE IF EXISTS region_fuel_type_age_with_thold;

    CREATE TABLE public.region_fuel_type_age_with_thold
    (
        id integer NOT NULL DEFAULT nextval('fuel_type_age_with_thold_id_seq'::regclass),
        fuel_type character varying COLLATE pg_catalog."default",
        yslb integer,
        geometry geometry(MultiPolygon,900914),
        shs boolean,
        cib boolean,
        lrr boolean,
        CONSTRAINT region_fuel_type_age_with_thold_pkey PRIMARY KEY (id)
    )

    TABLESPACE pg_default;

    ALTER TABLE public.fuel_type_age_with_thold
        OWNER to rfmp;

    DROP INDEX IF EXISTS public.region_fuel_type_age_with_thold_spat_idx;

    CREATE INDEX region_fuel_type_age_with_thold_spat_idx
        ON public.region_fuel_type_age_with_thold USING gist
        (geometry)
        TABLESPACE pg_default;
    
    DROP INDEX IF EXISTS public.region_idx_fuel_type_age_with_thold_fuel_type;

    CREATE INDEX region_idx_fuel_type_age_with_thold_fuel_type
        ON public.region_fuel_type_age_with_thold USING btree
        (fuel_type COLLATE pg_catalog."default" ASC NULLS LAST)
        TABLESPACE pg_default;
        
    DELETE FROM table_updates WHERE table_name = 'region_fuel_type_age_with_thold';
    INSERT INTO table_updates VALUES('region_fuel_type_age_with_thold', CURRENT_TIMESTAMP AT TIME ZONE 'australia/west');
    
    CREATE TRIGGER region_fuel_type_age_with_thold_update
    AFTER INSERT OR UPDATE OR DELETE ON region_fuel_type_age_with_thold 
    FOR EACH STATEMENT
    EXECUTE PROCEDURE update_table_updates();
    """

def create_region_fuel_type_age_with_thold_code():
    return """
    DROP TABLE IF EXISTS public.region_fuel_type_age_with_thold_code;

    CREATE TABLE public.region_fuel_type_age_with_thold
        fuel_type character varying COLLATE pg_catalog._code
    ("default",
        threshold_age integer,
        yslb integer,
        diff integer,
        target integer,
        geometry geometry(MultiPolygon,900914)
    )

    TABLESPACE pg_default;

    ALTER TABLE public.fuel_type_age_with_thold_code
        OWNER to rfmp;
    
    DROP INDEX IF EXISTS public.region_fuel_type_age_with_thold_code_geometry_geom_idx;

    CREATE INDEX region_fuel_type_age_with_thold_code_geometry_geom_idx
        ON public.region_fuel_type_age_with_thold_code USING gist
        (geometry)
        TABLESPACE pg_default;
    
    DROP INDEX IF EXISTS public.region_text_index;

    CREATE INDEX region_text_index
        ON public.region_fuel_type_age_with_thold_code USING btree
        (threshold_age ASC NULLS LAST, yslb ASC NULLS LAST, target ASC NULLS LAST)
        TABLESPACE pg_default;"""

def create_region_no_target():
    return """DROP TABLE IF EXISTS region_no_target;
    CREATE TABLE region_no_target 
    (
       id SERIAL PRIMARY KEY,
     fuel_type character varying(19) COLLATE pg_catalog."default",
    SHS boolean,
    CIB boolean,
    LRR boolean,
        geometry geometry(MultiPolygon,900914)
    )
    WITH (
        OIDS = FALSE
    )
    TABLESPACE pg_default;

    ALTER TABLE public.region_no_target OWNER to rfmp;

    DROP INDEX IF EXISTS public.region_no_target_spat_idx;

    CREATE INDEX region_no_target_spat_idx
        ON public.region_no_target USING gist
        (geometry)
        TABLESPACE pg_default;

    INSERT INTO region_no_target (fuel_type, geometry)
    SELECT fuel_type, geometry FROM region_fuel_type
    WHERE LOWER(fuel_type) NOT IN ('plantation', 'banksia woodland', 'thicket', 'sandplain shrubland');

    UPDATE region_no_target SET 
    SHS = True WHERE fuel_type in ('Acacia woodland', 'Semi arid woodland', 'Chenopod shrubland', 'Non-fuel');

    UPDATE region_no_target SET 
    CIB = True WHERE fuel_type in ('Acacia woodland', 'Semi arid woodland', 'Chenopod shrubland', 'Dry eucalypt forest', 'Wet eucalypt forest', 'Non-fuel');

    UPDATE region_no_target SET 
    LRR = True WHERE fuel_type in ('Acacia woodland', 'Semi arid woodland', 'Chenopod shrubland', 'Tropical savanna', 'Pindan', 'Hummock grassland', 'Mallee heath', 'Non-fuel');

    DELETE FROM table_updates WHERE table_name = 'region_no_target';
    INSERT INTO table_updates VALUES('region_no_target', CURRENT_TIMESTAMP AT TIME ZONE 'australia/west');
    
    CREATE TRIGGER trig_region_no_target_update
    AFTER INSERT OR UPDATE OR DELETE ON region_no_target 
    FOR EACH STATEMENT
    EXECUTE PROCEDURE update_table_updates();"""

def create_region_name_underlying_report_data_district_name():
    return """
    CREATE TABLE region_name_underlying_report_data_district_name AS
    (SELECT fma_type, fuel_type, threshold_age, yslb, target,
    CASE WHEN ST_Within(geometry, shape) THEN geometry
    WHEN ST_Overlaps(geometry, shape) THEN ST_Intersection(geometry, shape) END AS geometry
    FROM region_name_underlying_report_data, districts d
    WHERE d.admin_zone = 'district_name');
    
    CREATE INDEX idx_region_name_district_name ON region_name_underlying_report_data_district_name USING GIST(geometry);
    """

def create_regional_summary_report_data():
    # NO LONGER USED
    return """
    DROP TABLE IF EXISTS region_name_summary_report_data;
    CREATE TABLE public.region_name_summary_report_data
    (id serial primary key,
    region varchar(20),
    fma varchar(3),
    target integer,
    reached_th boolean,
    area float8)
    TABLESPACE pg_default;
    ALTER TABLE public.region_name_summary_report_data
        OWNER TO rfmp;
    """

def create_regional_summary_report_data_district():
    return """
    CREATE OR REPLACE VIEW public.region_name_summary_report_data_district
     AS
     SELECT 'region_name'::text AS region,
        region_name_underlying_report_data_district.fma_type,
        region_name_underlying_report_data_district.target,
            CASE
                WHEN region_name_underlying_report_data_district.yslb >= region_name_underlying_report_data_district.threshold_age THEN true
                ELSE false
            END AS reached_th,
        SUM(ST_Area(region_name_underlying_report_data_district.geometry)) / 10000::double precision AS area_ha
        FROM region_name_underlying_report_data_district
        GROUP BY 'region_name'::text, region_name_underlying_report_data_district.fma_type, region_name_underlying_report_data_district.target, (
            CASE
                WHEN region_name_underlying_report_data_district.yslb >= region_name_underlying_report_data_district.threshold_age THEN true
                ELSE false
            END);

    ALTER TABLE public.region_name_summary_report_data_district
        OWNER TO rfmp;
    """

def create_regional_summary_report_data_incl_zones():
    # Removed from usage 3-Mar-2020 with decision not to report on BRMZ, name changed from regional_areas_by_fma
    # Previously was called by rfm_library.get_report_data but may be able to delete
    return """
    DROP TABLE IF EXISTS region_name_summary_report_data;
    CREATE TABLE public.region_name_summary_report_data
    (id serial primary key,
    region varchar(20),
    zone varchar(50),
    fma varchar(3),
    target integer,
    reached_th boolean,
    area float8)
    TABLESPACE pg_default;
    ALTER TABLE public.region_name_summary_report_data
        OWNER TO rfmp;
    """

def create_threshold_table():
    # called by rfm_library.calculate_indic_tholds
    return """
    DROP VIEW IF EXISTS region_indic_thold_details;
    DROP VIEW IF EXISTS region_past_indic_thold;
    DROP TABLE IF EXISTS region_with_indic_thold;
    DROP INDEX IF EXISTS region_with_indic_thold_spat_idx;
    DROP INDEX IF EXISTS idx_region_with_indic_thold_threshold_age_yslb;
               
    CREATE TABLE public.region_with_indic_thold
    (id serial primary key,
    fma_type varchar(3),
    fuel_type  varchar(19) COLLATE pg_catalog."default",
    target integer,
    threshold_age integer,
    yslb integer,
    geometry geometry(Polygon, 900914))
    TABLESPACE pg_default;

    CREATE INDEX region_with_indic_thold_spat_idx ON region_with_indic_thold USING GIST(geometry);
    CREATE INDEX idx_region_with_indic_thold_threshold_age_yslb
        ON public.region_with_indic_thold USING btree
        (threshold_age, yslb)
        TABLESPACE pg_default;

    ALTER TABLE public.region_with_indic_thold
        OWNER TO rfmp;
        
    CREATE OR REPLACE VIEW region_indic_thold_details as select *, CASE
                WHEN region_with_indic_thold.yslb >= region_with_indic_thold.threshold_age AND region_with_indic_thold.threshold_age > 0 THEN true
                ELSE false
            END AS reached_th 
    FROM region_with_indic_thold;

    CREATE OR REPLACE VIEW region_past_indic_thold AS select *
    FROM region_with_indic_thold
    WHERE region_with_indic_thold.yslb >= region_with_indic_thold.threshold_age AND region_with_indic_thold.threshold_age > 0;
    """

def fill_region_fuel_type_age():
    return """
    DELETE FROM region_fuel_type_age;
    INSERT INTO region_fuel_type_age(fuel_type, yslb, geometry) 
    SELECT fuel_type, yslb, 
            CASE WHEN ST_CoveredBy(ft.geometry, fa.geometry) THEN ft.geometry
            WHEN ST_CoveredBy(fa.geometry, ft.geometry) THEN fa.geometry
            ELSE ST_MakeValid(PolygonalIntersection(ft.geometry, fa.geometry))
            END AS geometry
    FROM region_fuel_type ft, region_fuel_age fa
    WHERE ST_Intersects(ft.geometry, fa.geometry) AND NOT ST_Touches(ft.geometry, fa.geometry);
    UPDATE region_fuel_type_age SET area = ST_Area(geometry)/10000;
    DELETE FROM table_updates WHERE table_name = 'region_fuel_type_age';
    INSERT INTO table_updates VALUES('region_fuel_type_age', CURRENT_TIMESTAMP AT TIME ZONE 'australia/west');
    """

def fill_region_fuel_type_age_with_thold():
    return """
    INSERT INTO xregionx_fuel_type_age_with_thold(fuel_type, yslb, geometry, shs, cib, lrr)
    SELECT fuel_type, yslb, 
            CASE WHEN ST_CoveredBy(fta.geometry, r.geometry) THEN fta.geometry
            ELSE ST_MakeValid(PolygonalIntersection(fta.geometry, r.geometry))
            END AS geometry, 
            shs, cib, lrr
    FROM fuel_type_age_with_thold fta, regions r
    WHERE ST_Intersects(fta.geometry, r.geometry) AND NOT ST_Touches(fta.geometry, r.geometry) AND region = 'zregionz';
    UPDATE xregionx_fuel_type_age_with_thold SET shs = True WHERE fuel_type IN (SELECT fuel_type FROM xregionx_default_thresholds WHERE shs_target > -1 AND threshold_age > 0);
    UPDATE xregionx_fuel_type_age_with_thold SET shs = NULL WHERE fuel_type IN (SELECT fuel_type FROM xregionx_default_thresholds WHERE shs_target = -1 AND threshold_age = -1);
    UPDATE xregionx_fuel_type_age_with_thold SET cib = True WHERE fuel_type IN (SELECT fuel_type FROM xregionx_default_thresholds WHERE cib_target > -1 AND threshold_age > 0);
    UPDATE xregionx_fuel_type_age_with_thold SET cib = NULL WHERE fuel_type IN (SELECT fuel_type FROM xregionx_default_thresholds WHERE cib_target = -1 AND threshold_age = -1);
    UPDATE xregionx_fuel_type_age_with_thold SET lrr = True WHERE fuel_type IN (SELECT fuel_type FROM xregionx_default_thresholds WHERE lrr_target > -1 AND threshold_age > 0);
    UPDATE xregionx_fuel_type_age_with_thold SET lrr = NULL WHERE fuel_type IN (SELECT fuel_type FROM xregionx_default_thresholds WHERE lrr_target = -1 AND threshold_age = -1);
    
    DELETE FROM table_updates WHERE table_name = 'xregionx_fuel_type_age_with_thold';
    INSERT INTO table_updates VALUES ('xregionx_fuel_type_age_with_thold', CURRENT_TIMESTAMP AT TIME ZONE 'australia/west');
    """

def fill_region_fuel_type_age_with_thold_code():
    return """
    INSERT INTO region_fuel_type_age_with_thold_code(fuel_type, threshold_age, yslb, diff, target, geometry)
    SELECT f.fuel_type fuel_type, t.threshold_age threshold_age, f.yslb yslb, yslb - threshold_age diff, t.shs_target target, f.geometry geometry
    FROM region_fuel_type_age_with_thold f, region_default_thresholds t WHERE f.code = True AND t.shs_target > -1 AND f.fuel_type = t.fuel_type;
    
    INSERT INTO region_fuel_type_age_with_thold_code(fuel_type, threshold_age, yslb, diff, target, geometry)
    SELECT f.fuel_type fuel_type, t.threshold_age threshold_age, f.yslb yslb, yslb - threshold_age diff, t.cib_target target, f.geometry geometry
    FROM region_fuel_type_age_with_thold f, region_default_thresholds t WHERE f.code = True AND t.cib_target > -1 AND f.fuel_type = t.fuel_type;
    
    INSERT INTO region_fuel_type_age_with_thold_code(fuel_type, threshold_age, yslb, diff, target, geometry)
    SELECT f.fuel_type fuel_type, t.threshold_age threshold_age, f.yslb yslb, yslb - threshold_age diff, t.shs_target target, f.geometry geometry
    FROM region_fuel_type_age_with_thold f, region_default_thresholds t WHERE f.code = True AND t.lrr_target > -1 AND f.fuel_type = t.fuel_type;
    
    DELETE FROM table_updates WHERE table_name = 'region_fuel_type_age_with_thold_code';
    INSERT INTO table_updates VALUES ('region_fuel_type_age_with_thold_code', CURRENT_TIMESTAMP AT TIME ZONE 'australia/west');
    """

def find_overlapping_intersects():
    # called by rfm_library.handle_overlapping_intersects
    return """SELECT a.id, b.id, a.priority, b.priority
    FROM mytable a, mytable b
    WHERE a.ID < b.ID
    AND ST_Overlaps(a.geometry, b.geometry)
    AND ST_Area(ST_Intersection(a.geometry, b.geometry)) > 1;
    """

def regional_areas_by_fma():
    # called by rfm_library.get_report_data
    return """select fma_type,
    ST_Area(ST_Collect(p.geometry))/10000 AS Area_ha 
    FROM region_fmas_complete AS p 
    GROUP BY fma_type;
    """

def regional_areas_by_fma_incl_zones():
    # Removed from usage 3-Mar-2020 with decision not to report on BRMZ, name changed from regional_areas_by_fma
    # previously was called by rfm_library.get_report_data but may be able to delete
    return """select zone, fma_type,
    ST_Area(ST_Collect(case when ST_CoveredBy(p.geometry, z.geometry) then p.geometry
            else ST_MakeValid(PolygonalIntersection(p.geometry, z.geometry))
            END))/10000 AS Area_ha 
     FROM region_fmas_complete AS p 
       INNER JOIN brmzs_region AS z
        ON ST_Intersects(p.geometry,z.geometry)
    group by zone, fma_type;
    """

def regional_areas_with_indic_thold_details():
    # called by rfm_library.get_report_data
    return """select fma_type, target, reached_th,
    ST_Area(ST_Collect(td.geometry))/10000 AS Area_ha 
    FROM region_indic_thold_details AS td 
    GROUP BY fma_type, target, reached_th;
    """

def regional_areas_with_defin_thold_details():
    # called by rfm_library.get_report_data
    return """select fma_type, target, reached_th,
    ST_Area(ST_Collect(td.geometry))/10000 AS Area_ha 
    FROM region_thold_details AS td 
    GROUP BY fma_type, target, reached_th;
    """

def regional_areas_with_indic_thold_details_incl_zones():
    # Removed from usage 3-Mar-2020 with decision not to report on BRMZ, name changed from regional_areas_by_fma
    # previously was called by rfm_library.get_report_data but may be able to delete
    return """select zone, fma_type, target, reached_th,
    ST_Area(ST_Collect(case when ST_CoveredBy(td.geometry, z.geometry) then td.geometry
            else PolygonalIntersection(td.geometry, z.geometry)
            END))/10000 AS Area_ha 
     FROM region_indic_thold_details AS td 
       INNER JOIN brmzs_region AS z
        ON ST_Intersects(td.geometry,z.geometry)
    GROUP BY zone, fma_type, target, reached_th;
    """

def threshold_calculation_code():
    from rfm_library import debug_msg_box as debug
    debug("threshold_calculation_code (INDICATIVE)")
    # called by rfm_library.calculate_indic_tholds
    return """
    INSERT INTO region_with_indic_thold(fma_type, fuel_type, threshold_age, yslb, geometry)
    SELECT xyz.fma_type, xyz.fuel_type, xyz.threshold_age, xyz.yslb, xyz.geometry::geometry(Polygon,900914) AS geometry
    FROM (SELECT rfc.fma_type, t.fuel_type, t.threshold_age, t.yslb, (ST_Dump(PolygonalIntersection(ST_Buffer(rfc.geometry, 0.001), ST_Buffer(t.geometry, 0.001)))).geom AS geometry
        FROM region_fmas_complete rfc, fuel_type_age_with_thold_code t WHERE rfc.fma_type = 'CODE' AND ST_Intersects(rfc.geometry, t.geometry) AND NOT  st_touches(rfc.geometry, t.geometry)) AS xyz;
        
    INSERT INTO region_with_indic_thold(fma_type, fuel_type, threshold_age, yslb, geometry)
    SELECT xyz.fma_type, xyz.fuel_type, -1, -1, xyz.geometry::geometry(Polygon,900914) AS geometry
    FROM (SELECT rfc.fma_type, t.fuel_type, -1, -1, (ST_Dump(PolygonalIntersection(ST_Buffer(rfc.geometry, 0.001), ST_Buffer(t.geometry, 0.001)))).geom AS geometry
        FROM region_fmas_complete rfc, region_no_target t WHERE rfc.fma_type = 'CODE' AND t.CODE AND ST_Intersects(rfc.geometry, t.geometry) AND NOT  st_touches(rfc.geometry, t.geometry)) AS xyz;
    """

def threshold_calculation_last_part():
    from rfm_library import debug_msg_box as debug
    debug("threshold_calculation_last_part")
    return """       
    UPDATE region_with_indic_thold r SET target = (SELECT shs_target FROM fuel_type_indicative_thresholds f WHERE f.fuel_type = r.fuel_type) WHERE r.fma_type = 'SHS';
	UPDATE region_with_indic_thold r SET target = (SELECT cib_target FROM fuel_type_indicative_thresholds f WHERE f.fuel_type = r.fuel_type) WHERE r.fma_type = 'CIB';
	UPDATE region_with_indic_thold r SET target = (SELECT lrr_target FROM fuel_type_indicative_thresholds f WHERE f.fuel_type = r.fuel_type) WHERE r.fma_type = 'LRR';
    UPDATE region_with_indic_thold r SET target = -1 WHERE fuel_type = 'Non-fuel';
    """


#####DOMAINS#################################
def create_fma_domain():
    return """CREATE DOMAIN d_fma_types AS TEXT
        CHECK (VALUE IN ('SHS', 'CIB', 'LRR', 'RAM'));"""

def create_fuel_domain():
    return """CREATE DOMAIN d_fuel_types AS TEXT
        CHECK (VALUE IN ('Tropical savanna', 'Pindan', 'Hummock grassland', 'Sandplain shrubland', 'Thicket', 'Mallee heath', 'Dry eucalypt forest', 'Wet eucalypt forest', 'Banksia woodland', 'Plantation', 'Acacia woodland', 'Semi arid woodland', 'Chenopod woodland'));"""

def create_threshold_ages_domain():
    return """CREATE DOMAIN d_thold_ages AS INTEGER
        CHECK (VALUE = -1 OR VALUE > 0);"""
        
def create_targets_domain():
    return """CREATE DOMAIN d_targets AS INTEGER
        CHECK (VALUE = -1 OR (VALUE > 0 AND VALUE <= 100));"""
    

                

