CREATE FUNCTION [dbo].[GetValidToInContextInfo]()
RETURNS datetime
AS
BEGIN
	Declare @VALIDTO datetime
	Declare @MY_CONTEXT_INFO_TIME varchar(102)
	set @MY_CONTEXT_INFO_TIME = (select Cast(CONTEXT_INFO() as varchar(102)))
	IF(@MY_CONTEXT_INFO_TIME is null)
		BEGIN
			set @VALIDTO = GETUTCDATE()
		END
	ELSE
		BEGIN
			Declare @pos int      
			set @pos = CHARINDEX(N'|', @MY_CONTEXT_INFO_TIME, 0)
			IF(@pos = 0 or @pos is null)
				BEGIN
					set @VALIDTO = GETUTCDATE()
				END
			ELSE
				BEGIN
					set @VALIDTO = Convert(datetime, SUBSTRING(@MY_CONTEXT_INFO_TIME, @pos + 1, @pos - 1))
				END
		END
	return @VALIDTO
END