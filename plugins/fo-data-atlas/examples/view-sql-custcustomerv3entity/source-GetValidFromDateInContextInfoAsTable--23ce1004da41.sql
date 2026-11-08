CREATE   FUNCTION [dbo].[GetValidFromDateInContextInfoAsTable]()
RETURNS TABLE
AS
RETURN (select [dbo].[GetValidFromInContextInfo]() as [ValidFromInContextInfo]);