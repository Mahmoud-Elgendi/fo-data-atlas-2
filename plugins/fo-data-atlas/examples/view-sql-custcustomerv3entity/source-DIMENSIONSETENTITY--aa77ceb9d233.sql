CREATE VIEW [DBO].[DIMENSIONSETENTITY] AS SELECT T1.RECID AS RECORDID, T1.MAINACCOUNTVALUE AS MAINACCOUNT, T1.MODIFIEDDATETIME AS MODIFIEDDATETIME, T1.MODIFIEDBY AS MODIFIEDBY, T1.CREATEDDATETIME AS CREATEDDATETIME, T1.CREATEDBY AS CREATEDBY, T1.RECVERSION AS RECVERSION, T1.PARTITION AS PARTITION, T1.RECID AS RECID, (CAST ((
                SELECT (
                   SELECT CASE WHEN
                            NonNullDisplayValue IS NOT NULL
                            THEN NonNullDisplayValue
                            ELSE 'No active format for data entities has been set up.
Set up an active format for each dimension format type.'
                        END
                        FROM
                        (
                        -- Remove initial delimiter
                        SELECT STUFF(
                            (SELECT
                                    -- Prepend with delimiter and escape internal delimiters
                                    DIMENSIONSEGMENTDELIMITER + COALESCE(
                                        REPLACE(REPLACE(DIMLIST.DISPLAYVALUE, '\', '\\'),
                                                DIMENSIONSEGMENTDELIMITER,
                                                DIMENSIONSEGMENTDELIMITERESCAPED),
                                        '')
                                FROM
                                    (SELECT TOP (1) DH.RECID
                                        FROM DIMENSIONHIERARCHY DH
                                        JOIN DIMENSIONHIERARCHYINTEGRATION DHI
                                            ON DHI.DIMENSIONHIERARCHY = DH.RECID
                                            AND DHI.ISDEFAULT = 1
                                            AND DHI.PARTITION = T1.PARTITION
                                        WHERE
                                            DH.PARTITION = T1.PARTITION
                                            AND DH.STRUCTURETYPE = 17
                                    ) AS DH
                                JOIN DIMENSIONHIERARCHYLEVEL DHL
                                    ON DHL.DIMENSIONHIERARCHY = DH.RECID AND DHL.PARTITION = T1.PARTITION
                                JOIN DIMENSIONATTRIBUTE DA
                                    ON DA.RECID = DHL.DIMENSIONATTRIBUTE AND DA.PARTITION = T1.PARTITION
                                LEFT JOIN
                                        (SELECT DIMENSIONATTRIBUTE, DISPLAYVALUE
                                            FROM
                                                (SELECT * FROM DIMENSIONATTRIBUTEVALUESET DAVS
                                                    WHERE DAVS.PARTITION = T1.PARTITION AND DAVS.RECID = T1.RECID) P

                                            UNPIVOT
                                                (DISPLAYVALUE for DIMENSIONATTRIBUTE IN (ACCOUNTVALUE, AGREEMENTVALUE, BANKACCOUNTVALUE, BUSINESSUNITVALUE, BUSINESSUNIT_FRVALUE, CAMPAIGNVALUE, CARGOVALUE, CASHFLOW_CNVALUE, CENTERVALUE, CONDITIONVALUE, CONTRACTVALUE, COSTCENTERVALUE, COSTCENTER_CNVALUE, CUSTOMERVALUE, DEPARTMENTVALUE, DEPARTMENT_CNVALUE, DIVISIONVALUE, EXPENSEANDINCOMECODEVALUE, FILIALVALUE, FISCALESTABLISHMENTVALUE, FUNDVALUE, GROUPSVALUE, ITEMGROUPVALUE, JOBSKILLSVALUE, LABORTYPEVALUE, LEGALENTITYVALUE, LOCATIONVALUE, MAINACCOUNTVALUE, OBJECTCLASSVALUE, OWNERSHIP_CNVALUE, PRIMARY_VALUE, PRODUCTGROUPVALUE, PROGRAMVALUE, PROJECTVALUE, PURPOSEVALUE, PURPOSE_CNVALUE, RETAILCHANNELVALUE, SERVICELINEVALUE, STOREVALUE, SYSTEMGENERATEDATTRIBUTEBANKACCOUNTVALUE, SYSTEMGENERATEDATTRIBUTECUSTOMERVALUE, SYSTEMGENERATEDATTRIBUTEEMPLOYEEVALUE, SYSTEMGENERATEDATTRIBUTEEMPLOYEE_RUVALUE, SYSTEMGENERATEDATTRIBUTEFIXEDASSETS_RUVALUE, SYSTEMGENERATEDATTRIBUTEFIXEDASSETVALUE, SYSTEMGENERATEDATTRIBUTEITEMVALUE, SYSTEMGENERATEDATTRIBUTEPROJECTVALUE, SYSTEMGENERATEDATTRIBUTERCASHVALUE, SYSTEMGENERATEDATTRIBUTERDEFERRALSVALUE, SYSTEMGENERATEDATTRIBUTEVENDORVALUE, TAXBRANCHVALUE, TERMINALVALUE, VEHICLEVALUE, WORKERVALUE))
                                                        AS DIMENSIONVALUECOLUMNNAME
                                        ) AS DIMLIST 
                                    ON
                                        DIMLIST.DIMENSIONATTRIBUTE = REPLACE(DA.DIMENSIONVALUECOLUMNNAME COLLATE Database_Default, '.', '$')
                                ORDER BY DHL.DIMENSIONHIERARCHY, DHL.LEVEL_
                                FOR XML PATH(''), TYPE
                            ).value('(./text())[1]', 'NVARCHAR(MAX)'),
                            1, LEN(DIMENSIONSEGMENTDELIMITER), '')
                         AS NonNullDisplayValue)
                    AS DisplayValueFormat)
                    FROM
                        (SELECT TOP(1)
                                --Determine the account delimiter
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
                ) AS NVARCHAR(500))) AS DISPLAYVALUE FROM DIMENSIONATTRIBUTEVALUESET T1