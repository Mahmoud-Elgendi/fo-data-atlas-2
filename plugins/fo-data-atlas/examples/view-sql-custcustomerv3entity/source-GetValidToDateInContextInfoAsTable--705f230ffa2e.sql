CREATE   FUNCTION [dbo].[GetValidToDateInContextInfoAsTable]()
RETURNS TABLE
AS
RETURN (select [dbo].[GetValidToInContextInfo]() as [ValidToInContextInfo]);