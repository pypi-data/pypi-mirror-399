#!/usr/bin/env python3
#
#  __init__.py
"""
Toggle Git remotes between https and ssh.
"""
#
#  Copyright © 2020-2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
import re
from typing import Optional, Union

# 3rd party
import attr
import dulwich.repo
import southwark.repo
from apeye_core import URL
from domdf_python_tools.typing import PathLike
from typing_extensions import Literal

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2020 Dominic Davis-Foster"
__license__: str = "MIT License"
__version__: str = "0.1.2"
__email__: str = "dominic@davis-foster.co.uk"

__all__ = ["Remote", "Toggler"]


class Toggler(southwark.repo.Repo):  # noqa: PRM002
	"""
	Toggle Git remotes between https and ssh.

	:param repo: The repository to toggle remotes for.
	"""

	def __init__(self, repo: Union[dulwich.repo.Repo, PathLike], *args, **kwargs):
		if isinstance(repo, dulwich.repo.Repo):
			super().__init__(repo.path)
		else:
			super().__init__(repo)

	def get_current_remote(self, name: str = "origin") -> str:
		"""
		Return the current remote.

		:param name: If given, try to retrieve the remote with that name.
			If no such remote exists returns the ``origin`` remote.

		If no remote can be found an empty string will be returned.
		"""

		remotes = self.list_remotes()

		if name in remotes:
			return remotes[name]
		elif "origin" in remotes:
			return remotes["origin"]
		else:
			return ''

	def set_current_remote(self, url: Union[str, URL, "Remote"], name: str = "origin") -> None:
		"""
		Set the current remote.

		:param url: The URL to set for the remote.
		:param name: The name of the remote to set.
		"""

		if isinstance(url, Remote):
			url = url.as_url()

		config = self.get_config()

		if (b'remote', name.encode("UTF-8")) in config:
			del config[(b'remote', name.encode("UTF-8"))][b"url"]

		config.set(("remote", name), "url", str(url).encode("UTF-8"))

		config.write_to_path()


@attr.s
class Remote:
	"""
	Represents a remote repository.
	"""

	#: The style of remote.
	style: Literal["https", "ssh"] = attr.ib(converter=str, validator=attr.validators.in_(("https", "ssh")))

	#: The domain of the remote.
	domain: str = attr.ib(converter=str)

	#: The repository the remote points to.
	repo: str = attr.ib(converter=str)

	#: The account on the remote server which owns the repository.
	username: str = attr.ib(converter=str)

	def as_url(self) -> URL:
		"""
		Returns the :class:`apeye.url.URL` representation of the :class;`~.Remote`.

		:return:
		"""

		if self.style == "https":
			return URL(f"https://{self.domain}/{self.username}/{self.repo}.git")
		elif self.style == "ssh":
			return URL(f"git@{self.domain}:{self.username}/{self.repo}.git")

	@classmethod
	def from_url(cls, url: Union[str, URL]) -> "Remote":
		"""
		Construct a :class:`~.Remote` from a url.

		:param url:
		"""

		url = URL(url)

		if re.match(r"^\s*http(s)?://", str(url)):
			return cls(
					"https",
					domain=url.fqdn,
					repo=url.path.stem,
					username=str(url.path.parent)[1:],
					)

		elif re.match(r"^\s*git@", str(url)):
			domain = url.fqdn
			return cls(
					"ssh",
					domain=domain,
					repo=url.path.stem,
					username=str(url.netloc)[(len(domain) + 5):],
					)

		else:
			raise ValueError(f"Unknown remote type for {url}.")

	def set_username(self, username: Optional[str]) -> str:
		"""
		If ``username`` is not :py:obj:`None`, set :attr:`~.Remote.username` to that value.

		:param username:

		:return: The new value of :attr:`~.Remote.username`
		"""

		if username:
			self.username = username

		return self.username

	def set_repo(self, repo: Optional[str]) -> str:
		"""
		If ``repo`` is not :py:obj:`None`, set :attr:`~.Remote.repo` to that value.

		:param repo:

		:return: The new value of :attr:`~.Remote.repo`
		"""

		if repo:
			self.repo = repo

		return self.repo
