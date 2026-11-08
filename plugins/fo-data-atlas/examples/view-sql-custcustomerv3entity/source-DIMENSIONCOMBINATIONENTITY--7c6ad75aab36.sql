CREATE VIEW [DBO].[DIMENSIONCOMBINATIONENTITY] AS SELECT T1.RECID AS RECORDID, T1.SYSTEMGENERATEDJOURNALACCOUNT AS SYSTEMGENERATEDJOURNALACCOUNT, T1.SYSTEMGENERATEDJOURNALACCOUNTTYPE AS SYSTEMGENERATEDJOURNALACCOUNTTYPE, T1.SYSTEMGENERATEDJOURNALACCOUNTVALUE AS SYSTEMGENERATEDJOURNALACCOUNTVALUE, T1.MAINACCOUNTVALUE AS MAINACCOUNT, T1.MODIFIEDDATETIME AS MODIFIEDDATETIME, T1.MODIFIEDBY AS MODIFIEDBY, T1.CREATEDDATETIME AS CREATEDDATETIME, T1.CREATEDBY AS CREATEDBY, T1.RECVERSION AS RECVERSION, T1.PARTITION AS PARTITION, T1.RECID AS RECID, T2.NAME AS ACCOUNTSTRUCTURE, T2.RECVERSION AS RECVERSION#2, T2.PARTITION AS PARTITION#2, T2.RECID AS RECID#2, (CAST ((
                SELECT (
                    REPLACE(
                        REPLACE(
                            REPLACE(
                                CASE WHEN
                                    T1.LEDGERDIMENSIONTYPE != 1
AND SYSTEMGENERATEDATTRIBUTEBANKACCOUNT = 0
AND SYSTEMGENERATEDATTRIBUTECUSTOMER = 0
AND SYSTEMGENERATEDATTRIBUTEEMPLOYEE = 0
AND SYSTEMGENERATEDATTRIBUTEEMPLOYEE_RU = 0
AND SYSTEMGENERATEDATTRIBUTEFIXEDASSET = 0
AND SYSTEMGENERATEDATTRIBUTEFIXEDASSETS_RU = 0
AND SYSTEMGENERATEDATTRIBUTEITEM = 0
AND SYSTEMGENERATEDATTRIBUTEPROJECT = 0
AND SYSTEMGENERATEDATTRIBUTERCASH = 0
AND SYSTEMGENERATEDATTRIBUTERDEFERRALS = 0
AND SYSTEMGENERATEDATTRIBUTEVENDOR = 0
AND SYSTEMGENERATEDJOURNALACCOUNT = 0
AND SYSTEMGENERATEDJOURNALACCOUNTTYPE = 0
                                THEN
                                    (SELECT CASE WHEN 
                                        NonNullDisplayValue IS NOT NULL 
                                        THEN NonNullDisplayValue 
                                        ELSE 'No active format for data entities has been set up.
Set up an active format for each dimension format type.' 
                                    END
                                    FROM
                                    (SELECT (
                                        -- Remove initial delimiter
                                        STUFF(
                                            (SELECT
                                                -- Prepend with delimiter and escape internal delimiters
                                                DIMENSIONSEGMENTDELIMITER + COALESCE(
                                                        REPLACE(REPLACE(DIMLIST.COLUMNVALUE, '\', '\\'),
                                                        DIMENSIONSEGMENTDELIMITER,
                                                        DIMENSIONSEGMENTDELIMITERESCAPED),
                                                    '')
                                                FROM 
                                                    -- Get the dimension hierarchy
                                                    (SELECT TOP(1) DH.RECID
                                                        FROM DIMENSIONHIERARCHY DH
                                                        JOIN DIMENSIONHIERARCHYINTEGRATION DHI 
                                                                    ON DHI.DIMENSIONHIERARCHY = DH.RECID
                                                                    AND DHI.ISDEFAULT = 1
                                                                    AND DHI.PARTITION = T1.PARTITION
                                                        WHERE
                                                            DH.PARTITION = T1.PARTITION
                                                            AND DH.STRUCTURETYPE =
                                                                        CASE T1.LEDGERDIMENSIONTYPE
                                                                            WHEN 0 THEN 18
                                                                            WHEN 2 THEN 19
                                                                            WHEN 4 THEN 20
                                                                        END
                                                    ) AS DH
                                                JOIN DIMENSIONHIERARCHYLEVEL DHL 
                                                    ON DHL.DIMENSIONHIERARCHY = DH.RECID AND DHL.PARTITION = T1.PARTITION
                                                JOIN DIMENSIONATTRIBUTE DA 
                                                    ON DA.RECID = DHL.DIMENSIONATTRIBUTE AND DA.PARTITION = T1.PARTITION
                                                LEFT JOIN
                                                        (SELECT DIMENSIONATTRIBUTE, COLUMNVALUE
                                                            FROM
                                                                (SELECT * FROM DIMENSIONATTRIBUTEVALUECOMBINATION DAVC
                                                                    WHERE DAVC.PARTITION = T1.PARTITION AND DAVC.RECID = T1.RECID) P
                                                            UNPIVOT
                                                                (COLUMNVALUE for DIMENSIONATTRIBUTE IN (ACCOUNTVALUE, AGREEMENTVALUE, BANKACCOUNTVALUE, BUSINESSUNITVALUE, BUSINESSUNIT_FRVALUE, CAMPAIGNVALUE, CARGOVALUE, CASHFLOW_CNVALUE, CENTERVALUE, CONDITIONVALUE, CONTRACTVALUE, COSTCENTERVALUE, COSTCENTER_CNVALUE, CUSTOMERVALUE, DEPARTMENTVALUE, DEPARTMENT_CNVALUE, DIVISIONVALUE, EXPENSEANDINCOMECODEVALUE, FILIALVALUE, FISCALESTABLISHMENTVALUE, FUNDVALUE, GROUPSVALUE, ITEMGROUPVALUE, JOBSKILLSVALUE, LABORTYPEVALUE, LEGALENTITYVALUE, LOCATIONVALUE, MAINACCOUNTVALUE, OBJECTCLASSVALUE, OWNERSHIP_CNVALUE, PRIMARY_VALUE, PRODUCTGROUPVALUE, PROGRAMVALUE, PROJECTVALUE, PURPOSEVALUE, PURPOSE_CNVALUE, RETAILCHANNELVALUE, SERVICELINEVALUE, STOREVALUE, SYSTEMGENERATEDATTRIBUTEBANKACCOUNTVALUE, SYSTEMGENERATEDATTRIBUTECUSTOMERVALUE, SYSTEMGENERATEDATTRIBUTEEMPLOYEEVALUE, SYSTEMGENERATEDATTRIBUTEEMPLOYEE_RUVALUE, SYSTEMGENERATEDATTRIBUTEFIXEDASSETS_RUVALUE, SYSTEMGENERATEDATTRIBUTEFIXEDASSETVALUE, SYSTEMGENERATEDATTRIBUTEITEMVALUE, SYSTEMGENERATEDATTRIBUTEPROJECTVALUE, SYSTEMGENERATEDATTRIBUTERCASHVALUE, SYSTEMGENERATEDATTRIBUTERDEFERRALSVALUE, SYSTEMGENERATEDATTRIBUTEVENDORVALUE, SYSTEMGENERATEDJOURNALACCOUNTVALUE, TAXBRANCHVALUE, TERMINALVALUE, VEHICLEVALUE, WORKERVALUE)) AS DIMENSIONVALUECOLUMNNAME
                                                        ) AS DIMLIST
                                                    ON
                                                        DIMLIST.DIMENSIONATTRIBUTE = REPLACE(DA.DIMENSIONVALUECOLUMNNAME COLLATE Database_Default, '.', '$')
                                                ORDER BY DHL.DIMENSIONHIERARCHY, DHL.LEVEL_
                                                FOR XML PATH('')
                                            ),
                                            1, LEN(DIMENSIONSEGMENTDELIMITER), '')
                                        ) AS NonNullDisplayValue)
                                    AS DisplayValueFormat)
                                ELSE 
                                    -- Default or dynamic accounts
                                    (SELECT REPLACE(REPLACE(T1.DISPLAYVALUE, '\', '\\'),
                                                    DIMENSIONSEGMENTDELIMITER,
                                                    DIMENSIONSEGMENTDELIMITERESCAPED))
                                END
                                , '&amp;', '&')
                            , '&lt;', '<')
                        , '&gt;', '>')
                    )
                FROM
                    (SELECT TOP(1)
                            --Determine the segment delimiter
                            CASE DIMENSIONSEGMENTDELIMITER
                                WHEN 0 THEN '-'
WHEN 1 THEN '.'
WHEN 2 THEN '_'
WHEN 3 THEN '|'
WHEN 7 THEN '||'
WHEN 8 THEN '~'
WHEN 4 THEN '--'
WHEN 5 THEN '..'
WHEN 6 THEN '__'
WHEN 9 THEN '~~'

                            END AS DIMENSIONSEGMENTDELIMITER,
                            --Determine the account delimiter escaped
                            CASE DIMENSIONSEGMENTDELIMITER
                                WHEN 0 THEN '\-'
WHEN 1 THEN '\.'
WHEN 2 THEN '\_'
WHEN 3 THEN '\|'
WHEN 7 THEN '\|\|'
WHEN 8 THEN '\~'
WHEN 4 THEN '\-\-'
WHEN 5 THEN '\.\.'
WHEN 6 THEN '\_\_'
WHEN 9 THEN '\~\~'

                            END AS DIMENSIONSEGMENTDELIMITERESCAPED
                        FROM DIMENSIONPARAMETERS
                        WHERE DIMENSIONPARAMETERS.PARTITION = T1.PARTITION
                    ) AS DIMENSIONPARAMETERS
                ) AS NVARCHAR(500))) AS DISPLAYVALUE, (CAST (( CASE 
                        WHEN (T1.SYSTEMGENERATEDATTRIBUTEBANKACCOUNTVALUE != '') THEN T1.SYSTEMGENERATEDATTRIBUTEBANKACCOUNTVALUE
                        WHEN (T1.SYSTEMGENERATEDATTRIBUTECUSTOMERVALUE != '') THEN T1.SYSTEMGENERATEDATTRIBUTECUSTOMERVALUE
                        WHEN (T1.SYSTEMGENERATEDATTRIBUTEEMPLOYEEVALUE != '') THEN T1.SYSTEMGENERATEDATTRIBUTEEMPLOYEEVALUE
                        WHEN (T1.SYSTEMGENERATEDATTRIBUTEFIXEDASSETVALUE != '') THEN T1.SYSTEMGENERATEDATTRIBUTEFIXEDASSETVALUE
                        WHEN (T1.SYSTEMGENERATEDATTRIBUTEITEMVALUE != '') THEN T1.SYSTEMGENERATEDATTRIBUTEITEMVALUE
                        WHEN (T1.SYSTEMGENERATEDATTRIBUTEPROJECTVALUE != '') THEN T1.SYSTEMGENERATEDATTRIBUTEPROJECTVALUE
                        WHEN (T1.SYSTEMGENERATEDATTRIBUTEVENDORVALUE != '') THEN T1.SYSTEMGENERATEDATTRIBUTEVENDORVALUE
                        WHEN (T1.SYSTEMGENERATEDATTRIBUTEFIXEDASSETS_RUVALUE != '') THEN T1.SYSTEMGENERATEDATTRIBUTEFIXEDASSETS_RUVALUE
                        WHEN (T1.SYSTEMGENERATEDATTRIBUTERDEFERRALSVALUE != '') THEN T1.SYSTEMGENERATEDATTRIBUTERDEFERRALSVALUE
                        WHEN (T1.SYSTEMGENERATEDATTRIBUTERCASHVALUE != '') THEN T1.SYSTEMGENERATEDATTRIBUTERCASHVALUE
                        WHEN (T1.SYSTEMGENERATEDATTRIBUTEEMPLOYEE_RUVALUE != '') THEN T1.SYSTEMGENERATEDATTRIBUTEEMPLOYEE_RUVALUE ELSE '' END ) AS NVARCHAR(30))) AS ACCOUNTVALUE FROM DIMENSIONATTRIBUTEVALUECOMBINATION T1 LEFT OUTER JOIN DIMENSIONHIERARCHY T2 ON(( T1.ACCOUNTSTRUCTURE  =  T2.RECID)  AND ( T1.PARTITION  =  T2.PARTITION))