from typing import Iterator, Dict, Any
from pydantic import Field
import html
from ....core.action import BoardAction
from ....core.http import HTTPStream
from ....utils.logger import get_logger
from ....utils.clean_text import remove_html_tags

logger = get_logger()


class GetAllJobs(HTTPStream, BoardAction):
    board_token: str = Field(
        ...,
        description="Job Board URL token, which is usually the company `name` -for example `lyft`- when it has job listings on greenhouse, mandatory to access job boards on `greenhouse.io`: `https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs`, getting jobs doesn't require an API Key",
    )

    @property
    def base_url(self):
        return (
            "https://boards-api.greenhouse.io/v1/boards/{}/jobs/?content=true".format(
                self.board_token
            )
        )

    @property
    def http_method(self):
        return "GET"

    def pull(self) -> Iterator[Dict[str, Any]]:
        """
        pull all jobs from a greenhouse job board

        Returns:
            Iterator[Dict[str, Any]]: list of all jobs with their content if available
        """

        response = self.send_request()
        if response.status_code == 200:
            job_dict = response.json()
            total_info = job_dict["meta"]["total"]
            logger.info(f"Total jobs found : {total_info}")
            job_list = job_dict["jobs"]
            return job_list
        else:
            logger.error(
                f"Failed to get jobs from board: {self.board_token}, Check that your board token is valid"
            )
            error_message = "Unable to pull the data ! Reason : `{}`"
            raise ConnectionError(error_message.format(response.content))

    def format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        format each job pulled from greenhouse job board into a HrFlow job object

        Returns:
            Dict[str, Any]: job in the HrFlow job object format
        """

        job = dict()
        # name
        job["name"] = data.get("title")
        # summary
        job["summary"] = None
        # reference
        job["reference"] = str(data.get("id"))
        # url
        job["url"] = data.get("absolute_url")
        # location
        location = data.get("location").get("name")
        job["location"] = dict(text=location, lat=None, lng=None)
        # sections
        description_content = data.get("content")
        # convert the escaped description content into html format
        description_html = html.unescape(description_content)
        # remove html tags to get clean text
        text = remove_html_tags(description_html)

        job["sections"] = [
            dict(
                name="greenhouse_description",
                title="greenhouse_description",
                description=text,
            )
        ]
        # metadata
        job["metadatas"] = data.get("metadata")
        # tags
        department = data.get("departments")
        if department not in [None, []]:
            department_name = department[0].get("name")
            department_id = str(department[0].get("id"))
        else:
            department_name = "Undefined"
            department_id = "Undefined"

        office = data.get("offices")
        if office not in [None, []]:
            office_name = office[0].get("name")
            office_id = str(office[0].get("id"))
        else:
            office_name = "Undefined"
            office_id = "Undefined"

        education = data.get("education")
        employment = data.get("employment")

        job["tags"] = [
            dict(name="greenhouse_department-name", value=department_name),
            dict(name="greenhouse_department-id", value=department_id),
            dict(name="greenhouse_office-location", value=office_name),
            dict(name="greenhouse_office-id", value=office_id),
            dict(name="greenhouse_education", value=education),
            dict(name="greenhouse_employment", value=employment),
        ]
        # updated_at
        job["updated_at"] = data.get("updated_at")

        return job